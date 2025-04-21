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
        """Renderiza productos filtrados por categoría y ofertas."""
        offers = kwargs.get('offers', 'false').lower() == 'true'  # Verifica si 'offers=true' está en la URL
        domain = [('public_categ_ids', 'child_of', category.id), ('website_published', '=', True)]
        
        if offers:
            domain.append(('discounted_price', '>', 0))  # Filtrar productos con descuento
        
        # Buscar productos y categorías
        products = request.env['product.template'].sudo().search(domain)
        categories = request.env['product.public.category'].sudo().search([])

        return request.render('theme_xtream.offers_template', {
            'categories': categories,
            'discounted_products': products,
            'current_category': category,
            'offers': offers,
        })