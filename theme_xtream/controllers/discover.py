from odoo import http
from odoo.http import request

class DiscoverController(http.Controller):

    @http.route('/discover', type='http', auth='public', website=True)
    def website_discover(self, **kw):
        return request.render('theme_xtream.website_discover')