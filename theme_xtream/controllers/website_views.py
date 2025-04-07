from odoo import http
from odoo.http import request

class OffersController(http.Controller):

    @http.route('/offers', type='http', auth='public', website=True)
    def offers(self, **kwargs):
        """Renderiza la página de productos en oferta."""
        discounted_products = request.env['product.template'].sudo().search([
            ('website_published', '=', True),
            ('is_discounted', '=', True),  # Solo productos marcados como en oferta
            ('discount_percentage', '>', 0)  # Asegúrate de que tienen un descuento aplicado
        ])
        return request.render('theme_xtream.offers_template', {
            'discounted_products': discounted_products
        })