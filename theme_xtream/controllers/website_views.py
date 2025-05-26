from odoo import http
from odoo.http import request
from datetime import datetime as Datetime
from pytz import timezone

class OffersController(http.Controller):

    @http.route('/offers', type='http', auth='public', website=True)
    def offers(self, free_shipping=False, category_id=False, min_price=False, max_price=False, **kwargs):
        """Renderiza la página de productos en oferta."""

        # Convertir parámetros
        is_free_shipping = free_shipping == 'true'
        
        # Filtro base para productos
        domain = [
            ('website_published', '=', True),
            ('product_tag_ids', '!=', False),
        ]
        
        # Aplicar filtros
        if is_free_shipping:
            domain.append(('free_shipping', '=', True))
            
        if category_id:
            domain.append(('categ_id', 'child_of', int(category_id)))
            
        if min_price:
            domain.append(('discounted_price', '>=', float(min_price)))
            
        if max_price:
            domain.append(('discounted_price', '<=', float(max_price)))
            
        # IMPORTANTE: Usa el dominio con TODOS los filtros
        tagged_products = request.env['product.template'].sudo().search(domain)
        
        # El resto de tu código para filtrar productos...
        filtered_products = []
        for p in tagged_products:
            if p.website_published and p.product_tag_ids and p.product_tag_ids[0].start_date:
                filtered_products.append(p)
        
        # Ordenar productos...
        filtered_products = sorted(filtered_products, key=lambda p: p.product_tag_ids[0].start_date, reverse=True)
        
        # Aplicar dominio también a contadores de categorías
        all_categories = request.env['product.category'].sudo().search([])
        
        # Para cada categoría, incluir el filtro de free_shipping si está activo
        categories_with_count = []
        category_domain = [
            ('website_published', '=', True),
            ('product_tag_ids', '!=', False),
        ]
        
        if is_free_shipping:
            category_domain.append(('free_shipping', '=', True))
        
        for cat in all_categories:
            # Crear un dominio que incluya la categoría Y los filtros activos
            cat_domain = category_domain + [('categ_id', 'child_of', cat.id)]
            prod_count = request.env['product.template'].sudo().search_count(cat_domain)
            
            if prod_count > 0:
                # Incluir URL con todos los filtros activos
                url = f'/offers?category_id={cat.id}'
                if is_free_shipping:
                    url += '&free_shipping=true'
                    
                categories_with_count.append({
                    'id': cat.id,
                    'name': cat.name,
                    'product_count': prod_count,
                    'url': url  # URL que mantiene todos los filtros activos
                })
        
        # Price ranges también con el filtro de free_shipping
        price_domain = [
            ('website_published', '=', True),
            ('product_tag_ids', '!=', False),
        ]
        
        if is_free_shipping:
            price_domain.append(('free_shipping', '=', True))
        
        # Rangos de precio con filtros
        price_ranges = {
            '0_500': {
                'count': request.env['product.template'].sudo().search_count(
                    price_domain + [('discounted_price', '<=', 500)]
                ),
                'url': f'/offers?min_price=0&max_price=500{is_free_shipping and "&free_shipping=true" or ""}'
            },
            '500_1000': {
                'count': request.env['product.template'].sudo().search_count(
                    price_domain + [('discounted_price', '>', 500), ('discounted_price', '<=', 1000)]
                ),
                'url': f'/offers?min_price=500&max_price=1000{is_free_shipping and "&free_shipping=true" or ""}'
            },
            '1000_plus': {
                'count': request.env['product.template'].sudo().search_count(
                    price_domain + [('discounted_price', '>', 1000)]
                ),
                'url': f'/offers?min_price=1000{is_free_shipping and "&free_shipping=true" or ""}'
            },
        }
        
        
        # Obtener categorías principales (categorías sin padre)
        all_categories = request.env['product.category'].sudo().search([])
        main_categories = [
            cat for cat in all_categories
            if request.env['product.template'].sudo().search_count([
                ('website_published', '=', True),
                ('product_tag_ids', '!=', False),
                ('categ_id', 'child_of', cat.id)
            ]) > 0
        ]        # Solo productos publicados y que tengan al menos una etiqueta con start_date
        tagged_products = [p for p in tagged_products if p.website_published and p.product_tag_ids and p.product_tag_ids[0].start_date]

        # Ordenar por la fecha más reciente de start_date
        tagged_products = sorted(
            tagged_products,
            key=lambda p: p.product_tag_ids[0].start_date,
            reverse=True
        )
        # Calcular el total de productos publicados y con etiqueta
        total_products = request.env['product.template'].sudo().search_count([
            ('website_published', '=', True),
            ('product_tag_ids', '!=', False)
        ])
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
                    
        price_ranges = {
            '0_500': request.env['product.template'].sudo().search_count([
                ('website_published', '=', True),
                ('product_tag_ids', '!=', False),
                ('discounted_price', '>', 0),
                ('discounted_price', '<=', 500)
            ]),
            '500_1000': request.env['product.template'].sudo().search_count([
                ('website_published', '=', True),
                ('product_tag_ids', '!=', False),
                ('discounted_price', '>', 500),
                ('discounted_price', '<=', 1000)
            ]),
            '1000_plus': request.env['product.template'].sudo().search_count([
                ('website_published', '=', True),
                ('product_tag_ids', '!=', False),
                ('discounted_price', '>', 1000)
            ]),
        }
        # Obtener solo las categorías públicas que tengan al menos un producto con etiqueta

        categories_with_count = []
        for cat in main_categories:
            prod_count = request.env['product.template'].sudo().search_count([
                ('website_published', '=', True),
                ('product_tag_ids', '!=', False),
                ('categ_id', 'child_of', cat.id)
            ])
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
            'free_shipping': is_free_shipping,
            'category_id': category_id,
            'min_price': min_price,
            'max_price': max_price,
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

        domain = [
            ('website_published', '=', True),
            ('product_tag_ids', '!=', False)
        ]
        # Solo mostrar categorías principales que tengan productos con al menos un product.tag y categoría asignada
        all_categories = request.env['product.category'].sudo().search([])
        main_categories = [
            cat for cat in all_categories
            if request.env['product.template'].sudo().search_count([
                ('website_published', '=', True),
                ('product_tag_ids', '!=', False),
                ('categ_id', 'child_of', cat.id)
            ]) > 0
        ]
        categories_with_count = []
        for cat in main_categories:
            prod_count = request.env['product.template'].sudo().search_count([
                ('website_published', '=', True),
                ('product_tag_ids', '!=', False),
                ('categ_id', 'child_of', cat.id)
            ])
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
        
        if free_shipping:
            domain.append(('free_shipping', '=', True))
        
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

        if type_offer in ['day', 'flash']:
            filtered = []
            for p in products:
                for tag in p.product_tag_ids:
                    if tag.start_date and tag.end_date:
                        start = tag.start_date
                        end = tag.end_date
                        if isinstance(start, str):
                            start = Datetime.fromisoformat(start)
                        if isinstance(end, str):
                            end = Datetime.fromisoformat(end)
                        duration = (end - start).total_seconds() / 3600.0
                        if type_offer == 'day' and 23.5 <= duration <= 24.5:
                            filtered.append(p)
                            break  # Ya cumple, no revises más etiquetas
                        elif type_offer == 'flash' and 0 < duration <= 6:
                            filtered.append(p)
                            break
            products = filtered

        total_products = request.env['product.template'].sudo().search_count([
            ('website_published', '=', True),
            ('product_tag_ids', '!=', False)
        ])

        price_ranges = {
            '0_500': request.env['product.template'].sudo().search_count([
                ('website_published', '=', True),
                ('product_tag_ids', '!=', False),
                ('discounted_price', '>', 0),
                ('discounted_price', '<=', 500)
            ]),
            '500_1000': request.env['product.template'].sudo().search_count([
                ('website_published', '=', True),
                ('product_tag_ids', '!=', False),
                ('discounted_price', '>', 500),
                ('discounted_price', '<=', 1000)
            ]),
            '1000_plus': request.env['product.template'].sudo().search_count([
                ('website_published', '=', True),
                ('product_tag_ids', '!=', False),
                ('discounted_price', '>', 1000)
            ]),
        }

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


        })