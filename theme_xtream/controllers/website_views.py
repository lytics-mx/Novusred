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
        return request.render('theme_xtream.offers_template', {
            'discounted_products': tagged_products
        })