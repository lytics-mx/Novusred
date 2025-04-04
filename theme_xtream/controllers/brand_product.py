from odoo import http
from odoo.http import request

class BrandController(http.Controller):
    @http.route('/brand', auth='public', website=True)
    def brand_page(self, **kw):
        # Obtener productos publicados
        products = request.env['product.template'].sudo().search([('website_published', '=', True)])
        return request.render('theme_xtream_product_custom', {'products': products})