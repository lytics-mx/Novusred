from odoo import http
from odoo.http import request

class OffersController(http.Controller):

    @http.route('/offers', type='http', auth='public', website=True)
    def offers(self, **kwargs):
        """Renderiza la página de productos en oferta."""
        discounted_products = request.env['product.template'].sudo().search([
            ('website_published', '=', True),
            ('discount_price', '>', 0)  # Busca productos con precio de descuento mayor a 0
        ])
        return request.render('theme_xtream.offers_template', {
            'discounted_products': discounted_products
        })