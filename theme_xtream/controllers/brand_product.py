from odoo import http
from odoo.http import request

class BrandController(http.Controller):
    @http.route('/brand', auth='public', website=True)
    def brand_page(self, **kw):
        return http.request.render('theme_xtream.website_sale.product_custom')