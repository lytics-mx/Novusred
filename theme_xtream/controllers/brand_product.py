from odoo import http
from odoo.http import request

class WebsiteBrand(http.Controller):

    @http.route('/brand', auth='public', website=True)
    def home(self):
        return http.request.render('theme_xtream.website_brand')  