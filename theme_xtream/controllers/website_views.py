from odoo import http
from odoo.http import request

class OffersController(http.Controller):

    @http.route('/offers', type='http', auth='public', website=True)
    def offers(self, **kwargs):
        """Renderiza la página de productos en oferta."""
        # Filtrar productos publicados que tengan al menos una etiqueta
        tagged_products = request.env['product.template'].sudo().search([
            ('website_published', '=', True),
            ('product_tag_ids', '!=', False)  # Productos relacionados con etiquetas
        ])
    
        # Obtener categorías principales (categorías sin padre)
        main_categories = request.env['product.category'].sudo().search([('parent_id', '=', False)])
            # Ordenar por la fecha más reciente de start_date de la primera etiqueta (si existe)
        tagged_products = sorted(
            tagged_products,
            key=lambda p: p.product_tag_ids and p.product_tag_ids[0].start_date or Datetime.from_string('1970-01-01 00:00:00'),
            reverse=True
        )
        # Calcular el total de productos publicados
        total_products = request.env['product.template'].sudo().search_count([('website_published', '=', True)])

        # Calcular la cantidad de productos en cada rango de precios
        price_ranges = {
            '0_500': request.env['product.template'].sudo().search_count([
                ('website_published', '=', True),
                ('discounted_price', '<=', 500)
            ]),
            '500_1000': request.env['product.template'].sudo().search_count([
                ('website_published', '=', True),
                ('discounted_price', '>', 500),
                ('discounted_price', '<=', 1000)
            ]),
            '1000_plus': request.env['product.template'].sudo().search_count([
                ('website_published', '=', True),
                ('discounted_price', '>', 1000)
            ]),
        }
    
        return request.render('theme_xtream.offers_template', {
            'discounted_products': tagged_products,
            'categories': main_categories,
            'total_products': total_products,  # Total de productos publicados
            'price_ranges': price_ranges,  # Agregar price_ranges al contexto
        })

    @http.route(['/shop/category/<model("product.public.category"):category>', '/shop/category/all'], type='http', auth="public", website=True)
    def shop_by_category(self, category=None, **kwargs):
        """Renderiza productos filtrados por categoría y ofertas."""
        offers = kwargs.get('offers', 'false').lower() == 'true'
        free_shipping = kwargs.get('free_shipping', 'false').lower() == 'true'
        offer_type = kwargs.get('type')
        min_price = kwargs.get('min_price')
        max_price = kwargs.get('max_price')
    
        domain = [('website_published', '=', True)]
        
        if category:
            domain.append(('public_categ_ids', 'child_of', category.id))
        
        if offers:
            domain.append(('discounted_price', '>', 0))
        
        if free_shipping:
            domain.append(('free_shipping', '=', True))
        
        if offer_type:
            if offer_type == 'day':
                domain.append(('offer_type', '=', 'day'))
            elif offer_type == 'flash':
                domain.append(('offer_type', '=', 'flash'))
            elif offer_type == 'hour':
                domain.append(('offer_type', '=', 'hour'))
        
        if min_price:
            domain.append(('discounted_price', '>=', float(min_price)))
        
        if max_price:
            domain.append(('discounted_price', '<=', float(max_price)))
        
        # Buscar productos y categorías
        products = request.env['product.template'].sudo().search(domain)
        categories = request.env['product.public.category'].sudo().search([])
        total_products = request.env['product.template'].sudo().search_count([('website_published', '=', True)])
    
        return request.render('theme_xtream.offers_template', {
            'categories': categories,
            'discounted_products': products,
            'current_category': category,
            'offers': offers,
            'free_shipping': free_shipping,
            'total_products': total_products,  # Total de productos publicados
        })
    
    