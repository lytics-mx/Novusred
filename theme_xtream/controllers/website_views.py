from odoo import http
from odoo.http import request

class WebsiteShop(http.Controller):

    @http.route(['/shop/product/<model("product.template"):product>'], type='http', auth="public", website=True)
    def product(self, product, **kwargs):
        visited_product_ids = http.request.session.get('visited_product_ids', [])
        if product.id not in visited_product_ids:
            visited_product_ids.append(product.id)
            http.request.session['visited_product_ids'] = visited_product_ids[-5:]  # Mantener solo los últimos 5 productos
        return http.request.render("website_sale.product", {'product': product})