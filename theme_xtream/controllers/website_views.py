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
            if p.website_published and p.product_tag_ids and any(tag.start_date for tag in p.product_tag_ids):
                filtered_products.append(p)
        
        # Ordenar productos...
        filtered_products = sorted(filtered_products, 
                                   key=lambda p: p.product_tag_ids[0].start_date if p.product_tag_ids else Datetime.now(),
                                   reverse=True)
        
        # Obtener categorías principales
        all_categories = request.env['product.category'].sudo().search([])
        
        # IMPORTANTE: Crea un dominio base que incluya free_shipping si está activo
        base_domain = [
            ('website_published', '=', True),
            ('product_tag_ids', '!=', False),
        ]
        if is_free_shipping:
            base_domain.append(('free_shipping', '=', True))
            
        # Usa este dominio para todo
        main_categories = [
            cat for cat in all_categories
            if request.env['product.template'].sudo().search_count(base_domain + [('categ_id', 'child_of', cat.id)]) > 0
        ]
        
        # Para cada categoría, usar el mismo dominio base
        categories_with_count = []
        for cat in main_categories:
            prod_count = request.env['product.template'].sudo().search_count(base_domain + [('categ_id', 'child_of', cat.id)])
            if prod_count > 0:
                categories_with_count.append({
                    'id': cat.id,
                    'name': cat.name,
                    'product_count': prod_count,
                    'url': f'/offers?category_id={cat.id}{"&free_shipping=true" if is_free_shipping else ""}'
                })
    
        # Ofertas del día/relámpago filtradas también por free_shipping
        oferta_dia = []
        oferta_relampago = []
        
        for p in filtered_products:  # Ya incluye filtro de free_shipping
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
                        break 
                    elif 0 < duration <= 6:
                        oferta_relampago.append(p)
                        break
                        
        # Rangos de precio también con el filtro de free_shipping
        price_ranges = {}
        
        # Base domain para rangos de precio
        price_domain = base_domain.copy()  # Ya incluye free_shipping si está activo
        price_domain.append(('discounted_price', '>', 0))
        
        price_ranges = {
            '0_500': {
                'count': request.env['product.template'].sudo().search_count(
                    price_domain + [('discounted_price', '<=', 500)]
                ),
                'url': f'/offers?min_price=0&max_price=500{"&free_shipping=true" if is_free_shipping else ""}'
            },
            '500_1000': {
                'count': request.env['product.template'].sudo().search_count(
                    price_domain + [('discounted_price', '>', 500), ('discounted_price', '<=', 1000)]
                ),
                'url': f'/offers?min_price=500&max_price=1000{"&free_shipping=true" if is_free_shipping else ""}'
            },
            '1000_plus': {
                'count': request.env['product.template'].sudo().search_count(
                    price_domain + [('discounted_price', '>', 1000)]
                ),
                'url': f'/offers?min_price=1000{"&free_shipping=true" if is_free_shipping else ""}'
            },
        }
            
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
    def shop_by_category(self, free_shipping=False, category_id=False, min_price=False, max_price=False, **kwargs):
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
            if p.website_published and p.product_tag_ids and any(tag.start_date for tag in p.product_tag_ids):
                filtered_products.append(p)
        
        # Ordenar productos...
        filtered_products = sorted(filtered_products, 
                                key=lambda p: p.product_tag_ids[0].start_date if p.product_tag_ids else Datetime.now(),
                                reverse=True)
        
        # Obtener categorías principales
        all_categories = request.env['product.category'].sudo().search([])
        
        # IMPORTANTE: Crea un dominio base que incluya free_shipping si está activo
        base_domain = [
            ('website_published', '=', True),
            ('product_tag_ids', '!=', False),
        ]
        if is_free_shipping:
            base_domain.append(('free_shipping', '=', True))
            
        # Usa este dominio para todo
        main_categories = [
            cat for cat in all_categories
            if request.env['product.template'].sudo().search_count(base_domain + [('categ_id', 'child_of', cat.id)]) > 0
        ]
        
        # Para cada categoría, usar el mismo dominio base
        categories_with_count = []
        for cat in main_categories:
            prod_count = request.env['product.template'].sudo().search_count(base_domain + [('categ_id', 'child_of', cat.id)])
            if prod_count > 0:
                categories_with_count.append({
                    'id': cat.id,
                    'name': cat.name,
                    'product_count': prod_count,
                    'url': f'/offers?category_id={cat.id}{"&free_shipping=true" if is_free_shipping else ""}'
                })

        # Ofertas del día/relámpago filtradas también por free_shipping
        oferta_dia = []
        oferta_relampago = []
        
        for p in filtered_products:  # Ya incluye filtro de free_shipping
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
                        break 
                    elif 0 < duration <= 6:
                        oferta_relampago.append(p)
                        break
                        
        # Rangos de precio también con el filtro de free_shipping
        price_ranges = {}
        
        # Base domain para rangos de precio
        price_domain = base_domain.copy()  # Ya incluye free_shipping si está activo
        price_domain.append(('discounted_price', '>', 0))
        
        price_ranges = {
            '0_500': {
                'count': request.env['product.template'].sudo().search_count(
                    price_domain + [('discounted_price', '<=', 500)]
                ),
                'url': f'/offers?min_price=0&max_price=500{"&free_shipping=true" if is_free_shipping else ""}'
            },
            '500_1000': {
                'count': request.env['product.template'].sudo().search_count(
                    price_domain + [('discounted_price', '>', 500), ('discounted_price', '<=', 1000)]
                ),
                'url': f'/offers?min_price=500&max_price=1000{"&free_shipping=true" if is_free_shipping else ""}'
            },
            '1000_plus': {
                'count': request.env['product.template'].sudo().search_count(
                    price_domain + [('discounted_price', '>', 1000)]
                ),
                'url': f'/offers?min_price=1000{"&free_shipping=true" if is_free_shipping else ""}'
            },
        }
            
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