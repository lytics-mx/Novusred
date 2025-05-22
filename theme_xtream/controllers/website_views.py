from odoo import http
from odoo.http import request
from datetime import datetime as Datetime
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
        # Solo productos cuya primera etiqueta tenga start_date
        tagged_products = [p for p in tagged_products if p.product_tag_ids and p.product_tag_ids[0].start_date]

        # Ordenar por la fecha más reciente de start_date
        tagged_products = sorted(
            tagged_products,
            key=lambda p: p.product_tag_ids[0].start_date,
            reverse=True
        )
                # Calcular el total de productos publicados
        total_products = request.env['product.template'].sudo().search_count([('website_published', '=', True)])

        price_ranges = {
            '0_500': request.env['product.template'].sudo().search_count([
                ('website_published', '=', True),
                ('discounted_price', '>', 0),
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
            'total_products': total_products,
            'price_ranges': price_ranges,  # <-- ¡Agrega esto!
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
            tag = request.env['product.tag'].sudo().search([('name', 'ilike', offer_type)], limit=1)
            if tag:
                domain.append(('product_tag_ids', 'in', tag.id))
        
        if min_price:
            domain.append(('discounted_price', '>=', float(min_price)))
        
        if max_price:
            domain.append(('discounted_price', '<=', float(max_price)))
        
        # Buscar productos y categorías
        products = request.env['product.template'].sudo().search(domain)
        categories = request.env['product.public.category'].sudo().search([])
        total_products = request.env['product.template'].sudo().search_count([('website_published', '=', True)])
    
        price_ranges = {
            '0_500': request.env['product.template'].sudo().search_count([
                ('website_published', '=', True),
                ('discounted_price', '>', 0),
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
            'categories': categories,
            'discounted_products': products,
            'current_category': category,
            'offers': offers,
            'free_shipping': free_shipping,
            'total_products': total_products,
            'price_ranges': price_ranges,  # <-- ¡Agrega esto!
        })
    
    