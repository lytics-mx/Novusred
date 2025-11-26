from odoo import http
from odoo.http import request

class WishlistController(http.Controller):
    @http.route('/wishlist', type='http', auth='public', website=True)
    def wishlist_page(self):
        return request.render('theme_xtream.wishlist_template')

