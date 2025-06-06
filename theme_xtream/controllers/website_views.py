from odoo import http
from odoo.http import request
from datetime import datetime as Datetime
from pytz import timezone

class OffersController(http.Controller):

    @http.route('/offers', type='http', auth='public', website=True)
    def offers(self, free_shipping=False, **kwargs):
        tag_id = kwargs.get('tag_id')
        brand_type_id = kwargs.get('brand_type_id')
        offer_type = kwargs.get('type')
        min_price = kwargs.get('min_price')
        max_price = kwargs.get('max_price')
        type_offer = request.params.get('type')
        offers = kwargs.get('offers', 'false').lower() == 'true'

        domain = [
            ('website_published', '=', True),
            ('sale_ok', '=', True),
            '|',
            ('discount_percentage', '>', 0),
            ('fixed_discount', '>', 0)
        ]

        if tag_id:
            try:
                domain.append(('product_tag_ids', 'in', [int(tag_id)]))
            except Exception:
                pass

        if brand_type_id:
            try:
                domain.append(('brand_type_id', '=', int(brand_type_id)))
            except Exception:
                pass

        category_id = request.params.get('category_id')
        if category_id:
            domain.append(('categ_id', 'child_of', int(category_id)))
        if offers:
            domain.append(('discounted_price', '>', 0))

        if offer_type:
            tag = request.env['product.tag'].sudo().search([('name', 'ilike', offer_type)], limit=1)
            if tag:
                domain.append(('product_tag_ids', 'in', tag.id))

        if min_price:
            try:
                domain.append(('list_price', '>=', float(min_price)))
            except Exception:
                pass

        if max_price:
            try:
                domain.append(('list_price', '<=', float(max_price)))
            except Exception:
                pass

        # Filtro de envío gratis
        free_shipping = kwargs.get('free_shipping') == 'true'
        if free_shipping:
            domain.append(('free_shipping', '=', True))

        # Buscar productos filtrados
        products = request.env['product.template'].sudo().search(domain)
        # Calcular precios con descuento
        for product in products:
            if product.discount_percentage > 0:
                product.discounted_price = product.list_price * (1 - product.discount_percentage / 100)
            elif product.fixed_discount > 0:
                product.discounted_price = max(0, product.list_price - product.fixed_discount)
            else:
                product.discounted_price = product.list_price

        # Filtrar productos con descuento real
        discounted_products = products.filtered(lambda p: p.list_price > p.discounted_price)

        # Filtro de tipo de oferta (día, flash, current)
        if type_offer in ['day', 'flash', 'current']:
            filtered = []
            now = Datetime.now(timezone('America/Mexico_City'))
            for p in discounted_products:
                for tag in p.product_tag_ids:
                    if tag.start_date and tag.end_date:
                        start = tag.start_date
                        end = tag.end_date
                        if isinstance(start, str):
                            start = Datetime.fromisoformat(start)
                        if isinstance(end, str):
                            end = Datetime.fromisoformat(end)
                        if start.tzinfo is None:
                            start = start.replace(tzinfo=timezone('UTC')).astimezone(timezone('America/Mexico_City'))
                        if end.tzinfo is None:
                            end = end.replace(tzinfo=timezone('UTC')).astimezone(timezone('America/Mexico_City'))
                        duration = (end - start).total_seconds() / 3600.0
                        if type_offer == 'day' and 23.5 <= duration <= 24.5:
                            filtered.append(p)
                            break
                        elif type_offer == 'flash' and 0 < duration <= 6:
                            filtered.append(p)
                            break
                        elif type_offer == 'current' and start <= now <= end:
                            filtered.append(p)
                            break
            discounted_products = filtered

        # Obtener categorías principales
        all_categories = request.env['product.category'].sudo().search([])
        category_domain = [
            ('website_published', '=', True),
            ('product_tag_ids', '!=', False),
        ]
        if free_shipping:
            category_domain.append(('free_shipping', '=', True))
        main_categories = [
            cat for cat in all_categories
            if request.env['product.template'].sudo().search_count([
                *category_domain,
                ('categ_id', 'child_of', cat.id)
            ]) > 0
        ]

        # Obtener marcas principales con conteo de productos con descuento
        Brand = request.env['product.brand.type'].sudo()
        all_brands = Brand.search([])
        brands_with_count = []
        for brand in all_brands:
            brand_domain = list(domain) + [('brand_type_id', '=', brand.id)]
            brand_products = request.env['product.template'].sudo().search(brand_domain)
            brand_products_with_discount = brand_products.filtered(lambda p: p.list_price > p.discounted_price)
            if brand_products_with_discount:
                brands_with_count.append({
                    'id': brand.id,
                    'name': brand.name,
                    'product_count': len(brand_products_with_discount),
                })

        # Obtener tags principales
        product_tags = request.env['product.tag'].sudo().search([
            ('visible_on_ecommerce', '=', True)
        ], limit=6)

        # Rango de precios
        price_ranges = {
            '0_500': len([p for p in discounted_products if 0 < p.discounted_price <= 500]),
            '500_1000': len([p for p in discounted_products if 500 < p.discounted_price <= 1000]),
            '1000_plus': len([p for p in discounted_products if p.discounted_price > 1000]),
        }

        # Total de productos con descuento
        total_products = len(discounted_products)

        # Tags con descuento real
        ProductTag = request.env['product.tag'].sudo()
        tags_with_discount = []
        for tag in ProductTag.search([('visible_on_ecommerce', '=', True)]):
            prods = request.env['product.template'].sudo().search([
                ('website_published', '=', True),
                ('product_tag_ids', 'in', tag.id),
                ('discount_percentage', '>', 0)
            ])
            if prods:
                tags_with_discount.append(tag)

        return request.render('theme_xtream.offers_template', {
            'discounted_products': discounted_products,
            'categories_with_count': [
                {
                    'id': cat.id,
                    'name': cat.name,
                    'product_count': request.env['product.template'].sudo().search_count([
                        ('website_published', '=', True),
                        ('product_tag_ids', '!=', False),
                        ('categ_id', 'child_of', cat.id),
                        ('list_price', '>', 0),
                        '|',
                        ('discount_percentage', '>', 0),
                        ('fixed_discount', '>', 0)
                    ])
                } for cat in main_categories
            ],
            'brands_with_count': brands_with_count,
            'total_products': total_products,
            'price_ranges': price_ranges,
            'all_categories': main_categories,
            'free_shipping': free_shipping,
            'tags_with_discount': tags_with_discount,
            'product_tags': product_tags,
            'selected_tag_id': tag_id,
            'selected_brand_type_id': brand_type_id,
            'offer_type': offer_type,
            'min_price': min_price,
            'max_price': max_price,
            'type_offer': type_offer,
        })


    @http.route(['/shop/category/<model("product.public.category"):category>', '/shop/category/all'], type='http', auth="public", website=True)
    def shop_by_category(self, category=None, **kwargs):
        """Renderiza productos filtrados por categoría y ofertas."""
        offers = kwargs.get('offers', 'false').lower() == 'true'
        free_shipping = kwargs.get('free_shipping', 'false').lower() == 'true'
        offer_type = kwargs.get('type')
        min_price = kwargs.get('min_price')
        max_price = kwargs.get('max_price')
        type_offer = request.params.get('type')
        tag_id = kwargs.get('tag_id')
        brand_type_id = kwargs.get('brand_type_id')

 
        # Guardar el estado de free_shipping en la sesión del usuario
        # para mantenerlo entre diferentes páginas y filtros
        if 'free_shipping' in kwargs:
            request.session['free_shipping'] = free_shipping
        else:
            # Si no viene en los parámetros, usar el valor guardado en sesión (si existe)
            free_shipping = request.session.get('free_shipping', False)
    
        domain = [
            ('website_published', '=', True),
            ('sale_ok', '=', True),
            '|',
            ('discount_percentage', '>', 0),
            ('fixed_discount', '>', 0)
        ]
        
        # Aplicar filtro de free_shipping si está activo
        if free_shipping:
            domain.append(('free_shipping', '=', True))
        
        # Crear dominio para categorías
        category_domain = [
            ('website_published', '=', True),
            ('product_tag_ids', '!=', False),
        ]
        
        if free_shipping:
            category_domain.append(('free_shipping', '=', True))
        
        # Solo mostrar categorías principales que tengan productos según los filtros actuales
        all_categories = request.env['product.category'].sudo().search([])
        main_categories = [
            cat for cat in all_categories
            if request.env['product.template'].sudo().search_count([
                *category_domain,
                ('categ_id', 'child_of', cat.id)
            ]) > 0
        ]
        product_tags = request.env['product.tag'].sudo().search([
            ('visible_on_ecommerce', '=', True)  # Solo los visibles en ecommerce
        ], limit=6)

        categories_with_count = []
        for cat in main_categories:
            cat_domain = [
                ('website_published', '=', True),
                ('product_tag_ids', '!=', False),
                ('categ_id', 'child_of', cat.id)
            ]
            
            if free_shipping:
                cat_domain.append(('free_shipping', '=', True))
                
            # Obtener productos de la categoría y filtrar por descuento real
            cat_products = request.env['product.template'].sudo().search(cat_domain)
            cat_products_with_discount = cat_products.filtered(lambda p: p.list_price > p.discounted_price)
            prod_count = len(cat_products_with_discount)
            
            if prod_count > 0:  # Solo incluir categorías con productos que cumplan el filtro
                categories_with_count.append({
                    'id': cat.id,
                    'name': cat.name,
                    'product_count': prod_count,
                })
                    
        category_id = request.params.get('category_id')
        if category_id:
            domain.append(('categ_id', 'child_of', int(category_id)))
        
        if offers:
            domain.append(('discounted_price', '>', 0))
        
        if offer_type:
            tag = request.env['product.tag'].sudo().search([('name', 'ilike', offer_type)], limit=1)
            if tag:
                domain.append(('product_tag_ids', 'in', tag.id))
        
        if min_price:
            try:
                domain.append(('list_price', '>=', float(min_price)))
            except Exception:
                pass

        if max_price:
            try:
                domain.append(('list_price', '<=', float(max_price)))
            except Exception:
                pass
        if tag_id:
            try:
                domain.append(('product_tag_ids', 'in', [int(tag_id)]))
            except Exception:
                pass

        if brand_type_id:
            try:
                domain.append(('brand_type_id', '=', int(brand_type_id)))
            except Exception:
                pass       
        # IMPORTANTE: Primero BUSCAR los productos
        products = request.env['product.template'].sudo().search(domain)
        
        # LUEGO filtrar por descuento real
        products = products.filtered(lambda p: p.list_price > p.discounted_price)
        
        
        # Si estás procesando tiempos restantes, mantener solo productos con descuento real
        if type_offer in ['day', 'flash', 'current']:
        
            filtered = []
            remaining_times = {}  # Diccionario para almacenar los tiempos restantes
            now = Datetime.now(timezone('America/Mexico_City'))
            
            for p in products:
                for tag in p.product_tag_ids:
                    if tag.start_date and tag.end_date:
                        start = tag.start_date
                        end = tag.end_date
                        if isinstance(start, str):
                            start = Datetime.fromisoformat(start)
                        if isinstance(end, str):
                            end = Datetime.fromisoformat(end)
                        
                        # Convertir a objetos datetime conscientes de la zona horaria
                        if start.tzinfo is None:
                            start = start.replace(tzinfo=timezone('UTC'))
                            start = start.astimezone(timezone('America/Mexico_City'))
                        if end.tzinfo is None:
                            end = end.replace(tzinfo=timezone('UTC'))
                            end = end.astimezone(timezone('America/Mexico_City'))
                        
                        duration = (end - start).total_seconds() / 3600.0
                        
                        if type_offer == 'day' and 23.5 <= duration <= 24.5:
                            filtered.append(p)
                            break  # Ya cumple, no revises más etiquetas
                        elif type_offer == 'flash' and 0 < duration <= 6:
                            filtered.append(p)
                            break
                        elif type_offer == 'current' and start <= now <= end:
                            # Para ofertas activas actualmente
                            filtered.append(p)
                            # Calcular tiempo restante
                            remaining_time = end - now
                            remaining_hours = int(remaining_time.total_seconds() / 3600)
                            remaining_minutes = int((remaining_time.total_seconds() % 3600) / 60)
                            # Almacenar en el diccionario usando el ID del producto como clave
                            remaining_times[p.id] = f"{remaining_hours}h {remaining_minutes}m"
                            break
            products = filtered
    
        # Calcular el total de productos según los filtros actuales
        total_domain = [
            ('website_published', '=', True),
            ('product_tag_ids', '!=', False)
        ]
        
        if free_shipping:
            total_domain.append(('free_shipping', '=', True))
            
        total_products = request.env['product.template'].sudo().search_count(total_domain)
    
        # Actualizar los contadores de rango de precios según el filtro de free_shipping
        price_range_domain = [
            ('website_published', '=', True),
            ('product_tag_ids', '!=', False),
        ]
        
        if free_shipping:
            price_range_domain.append(('free_shipping', '=', True))

        # Obtener todos los productos y filtrar por descuento real
        all_products = request.env['product.template'].sudo().search(price_range_domain)
        discounted_products = all_products.filtered(lambda p: p.list_price > p.discounted_price)
        
        # SOLO UNA definición de price_ranges - ELIMINA LA DUPLICADA
        price_ranges = {
            '0_500': len(discounted_products.filtered(lambda p: 0 < p.discounted_price <= 500)),
            '500_1000': len(discounted_products.filtered(lambda p: 500 < p.discounted_price <= 1000)),
            '1000_plus': len(discounted_products.filtered(lambda p: p.discounted_price > 1000)),
        }

        # Calcular total correcto
        all_total_products = request.env['product.template'].sudo().search(total_domain)
        total_products_with_discount = all_total_products.filtered(lambda p: p.list_price > p.discounted_price)
        ProductTag = request.env['product.tag'].sudo()
        tags_with_discount = []
        for tag in ProductTag.search([('visible_on_ecommerce', '=', True)]):
            # Busca productos con este tag y descuento real
            prods = request.env['product.template'].sudo().search([
                ('website_published', '=', True),
                ('product_tag_ids', 'in', tag.id),
                ('discount_percentage', '>', 0)
            ])
            if prods:
                tags_with_discount.append(tag)    
                
        return request.render('theme_xtream.offers_template', {
            'discounted_products': products,
            'current_category': category,
            'offers': offers,
            'free_shipping': free_shipping,
            'total_products': len(total_products_with_discount),  # Usar el conteo correcto
            'price_ranges': price_ranges,
            'offer_type': offer_type,
            'categories_with_count': categories_with_count,
            'all_categories': main_categories,
            'product_tags': product_tags,
            'tags_with_discount': tags_with_discount,
            'selected_tag_id': tag_id,
            'selected_brand_type_id': brand_type_id,

        })