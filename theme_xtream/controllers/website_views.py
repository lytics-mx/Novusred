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

        return request.render('theme_xtream.offers_template', {
            'discounted_products': tagged_products,
            'categories': main_categories
        })
    

    @http.route(['/shop/category/<model("product.public.category"):category>'], type='http', auth="public", website=True)
    def shop_by_category(self, category, **kwargs):
        offers = kwargs.get('offers', False)
        domain = [('public_categ_ids', 'child_of', category.id)]
        
        if offers:
            domain.append(('discounted_price', '>', 0))  # Filtrar productos con descuento
        
        products = request.env['product.template'].search(domain)
        return request.render('theme_xtream.offers_template', {
            'categories': request.env['product.public.category'].search([]),
            'discounted_products': products,
        })
