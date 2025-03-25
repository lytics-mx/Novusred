from odoo import http
from odoo.http import request

import logging
_logger = logging.getLogger(__name__)

class WebsiteShop(http.Controller):

    @http.route('/lg', auth='public', website=True)
    def marcas_lg(self, **kw):
        return http.request.render('theme_xtream.marcas_lg')

    @http.route(['/shop/visited_products'], type='http', auth="public", website=True)
    def visited_products(self, **kwargs):
        visited_product_ids = http.request.session.get('visited_product_ids', [])
        visited_products = request.env['product.template'].browse(visited_product_ids)
        return http.request.render("theme_xtream.visited_products", {'visited_products': visited_products})
    

