from odoo import http
from odoo.http import request
from datetime import datetime as Datetime, timedelta
from pytz import timezone

class OffersController(http.Controller):

    @http.route('/offers', type='http', auth='public', website=True)
    def offers(self, free_shipping=False, **kwargs):
        """Renderiza la página de productos en oferta."""
    
        # Guardar el estado de free_shipping en la sesión del usuario
        if 'free_shipping' in request.params:
            free_shipping = request.params.get('free_shipping') == 'true'
            request.session['free_shipping'] = free_shipping
        else:
            # Si no viene en los parámetros, usar el valor guardado en sesión (si existe)
            free_shipping = request.session.get('free_shipping', False)
    
        # Filtro base para productos publicados con etiquetas
        domain = [
            ('website_published', '=', True),
            ('product_tag_ids', '!=', False),
        ]
        
        # Si el checkbox está marcado, agregar filtro de free_shipping
        if free_shipping:
            domain.append(('free_shipping', '=', True))    
        
        # IMPORTANTE: USA EL DOMAIN CON EL FILTRO free_shipping
        tagged_products = request.env['product.template'].sudo().search(domain)
        
        # Solo productos que tengan al menos una etiqueta con start_date
        filtered_products = []
        for p in tagged_products:
            if p.website_published and p.product_tag_ids and p.product_tag_ids[0].start_date:
                filtered_products.append(p)
    
        # Ordenar por la fecha más reciente de start_date
        filtered_products = sorted(
            filtered_products,
            key=lambda p: p.product_tag_ids[0].start_date,
            reverse=True
        )
        
        # Obtener categorías principales (categorías sin padre)
        all_categories = request.env['product.category'].sudo().search([])
        
        # Crear el dominio para filtrar categorías
        category_domain = [
            ('website_published', '=', True),
            ('product_tag_ids', '!=', False),
        ]
        
        # Aplicar filtro de free_shipping al dominio de categorías si está activo
        if free_shipping:
            category_domain.append(('free_shipping', '=', True))
        
        main_categories = [
            cat for cat in all_categories
            if request.env['product.template'].sudo().search_count([
                *category_domain,
                ('categ_id', 'child_of', cat.id)
            ]) > 0
        ]
        
        # Solo productos publicados y que tengan al menos una etiqueta con start_date
        tagged_products = [p for p in tagged_products if p.website_published and p.product_tag_ids and p.product_tag_ids[0].start_date]
    
        # Ordenar por la fecha más reciente de start_date
        tagged_products = sorted(
            tagged_products,
            key=lambda p: p.product_tag_ids[0].start_date,
            reverse=True
        )
        # Obtener todas las etiquetas activas que tienen productos asociados
        product_tags = request.env['product.tag'].sudo().search([
            ('is_active', '=', True),
            ('discount_percentage', '>', 0)
        ])
        
        # Filtrar solo las etiquetas que están asociadas a productos visibles
        valid_tags = []
        for tag in product_tags:
            tag_products = request.env['product.template'].sudo().search([
                ('visible_on_ecommerce', '=', True),
                ('product_tag_ids', 'in', tag.id)
            ], limit=1)
            
            if tag_products:
                valid_tags.append(tag)
                        
        # Calcular el total de productos publicados y con etiqueta
        total_domain = [
            ('website_published', '=', True),
            ('product_tag_ids', '!=', False)
        ]
        if free_shipping:
            total_domain.append(('free_shipping', '=', True))
            
        total_products = request.env['product.template'].sudo().search_count(total_domain)
        
        oferta_dia = []
        oferta_relampago = []
        for p in tagged_products:
            for tag in p.product_tag_ids:
                if tag.start_date and tag.end_date:
                    start = tag.start_date
                    end = tag.end_date
                    if isinstance(start, str):
                        start = Datetime.fromisoformat(start)
                    if isinstance(end, str):
                        end = Datetime.fromisoformat(end)
                    duration = (end - start).total_seconds() / 3600.0
                    if 23.5 <= duration <= 24.5:
                        oferta_dia.append(p)
                        break  # Ya cumple, no revises más etiquetas
                    elif 0 < duration <= 6:
                        oferta_relampago.append(p)
                        break
                        
        # Actualizar los contadores de rango de precios según el filtro de free_shipping
        price_range_domain = [
            ('website_published', '=', True),
            ('product_tag_ids', '!=', False),
        ]
        
        if free_shipping:
            price_range_domain.append(('free_shipping', '=', True))
            
        price_ranges = {
            '0_500': request.env['product.template'].sudo().search_count([
                *price_range_domain,
                ('discounted_price', '>', 0),
                ('discounted_price', '<=', 500)
            ]),
            '500_1000': request.env['product.template'].sudo().search_count([
                *price_range_domain,
                ('discounted_price', '>', 500),
                ('discounted_price', '<=', 1000)
            ]),
            '1000_plus': request.env['product.template'].sudo().search_count([
                *price_range_domain,
                ('discounted_price', '>', 1000)
            ]),
        }
        
        # Obtener solo las categorías públicas que tengan al menos un producto con etiqueta
        categories_with_count = []
        for cat in main_categories:
            cat_domain = [
                ('website_published', '=', True),
                ('product_tag_ids', '!=', False),
                ('categ_id', 'child_of', cat.id)
            ]
            
            if free_shipping:
                cat_domain.append(('free_shipping', '=', True))
                
            prod_count = request.env['product.template'].sudo().search_count(cat_domain)
            
            if prod_count > 0:  # Solo incluir categorías con productos que cumplan el filtro
                categories_with_count.append({
                    'id': cat.id,
                    'name': cat.name,
                    'product_count': prod_count,
                })
                
        return request.render('theme_xtream.offers_template', {
            'discounted_products': filtered_products,
            'categories_with_count': categories_with_count,
            'total_products': len(filtered_products),
            'price_ranges': price_ranges,
            'oferta_dia': oferta_dia,
            'oferta_relampago': oferta_relampago,
            'all_categories': main_categories,
            'free_shipping': free_shipping,  # Ahora es un booleano, no una cadena
            'valid_tags': valid_tags,  # Pasar las etiquetas válidas al contexto
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
    
        # Guardar el estado de free_shipping en la sesión del usuario
        # para mantenerlo entre diferentes páginas y filtros
        if 'free_shipping' in kwargs:
            request.session['free_shipping'] = free_shipping
        else:
            # Si no viene en los parámetros, usar el valor guardado en sesión (si existe)
            free_shipping = request.session.get('free_shipping', False)
    
        domain = [
            ('website_published', '=', True),
            ('product_tag_ids', '!=', False)
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
        
        categories_with_count = []
        for cat in main_categories:
            cat_domain = [
                ('website_published', '=', True),
                ('product_tag_ids', '!=', False),
                ('categ_id', 'child_of', cat.id)
            ]
            
            if free_shipping:
                cat_domain.append(('free_shipping', '=', True))
                
            prod_count = request.env['product.template'].sudo().search_count(cat_domain)
            
            if prod_count > 0:  # Solo incluir categorías que tengan productos con el filtro actual
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
            domain.append(('discounted_price', '>=', float(min_price)))
        
        if max_price:
            domain.append(('discounted_price', '<=', float(max_price)))
    
        # Buscar productos y categorías
        products = request.env['product.template'].sudo().search(domain)
    
        # Inicializar remaining_times antes del bloque condicional
        remaining_times = {}  # Diccionario para almacenar los tiempos restantes
        
        if type_offer in ['day', 'flash', 'current']:
            filtered = []
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
    
        # Actualizar los price_ranges según el filtro de free_shipping
        price_range_domain = [
            ('website_published', '=', True),
            ('product_tag_ids', '!=', False),
        ]
        
        if free_shipping:
            price_range_domain.append(('free_shipping', '=', True))
            
        price_ranges = {
            '0_500': request.env['product.template'].sudo().search_count([
                *price_range_domain,
                ('discounted_price', '>', 0),
                ('discounted_price', '<=', 500)
            ]),
            '500_1000': request.env['product.template'].sudo().search_count([
                *price_range_domain,
                ('discounted_price', '>', 500),
                ('discounted_price', '<=', 1000)
            ]),
            '1000_plus': request.env['product.template'].sudo().search_count([
                *price_range_domain,
                ('discounted_price', '>', 1000)
            ]),
        }
    
        # Asegurarse de que el valor de free_shipping se pase a la plantilla
        return request.render('theme_xtream.offers_template', {
            'discounted_products': products,
            'current_category': category,
            'offers': offers,
            'free_shipping': free_shipping,
            'total_products': total_products,
            'price_ranges': price_ranges,
            'offer_type': offer_type,
            'categories_with_count': categories_with_count,
            'all_categories': main_categories,
            'remaining_times': remaining_times,  # Añadir el diccionario al contexto
            'datetime': Datetime,  # Necesario para usar datetime en la plantilla
            'timedelta': timedelta,  # Si también necesitas timedelta
        })