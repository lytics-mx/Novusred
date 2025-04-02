from odoo import http
from odoo.http import request

class ShopController(http.Controller):

    @http.route(['/shop/product/<model("product.product"):product>'], type='http', auth="public", website=True)
    def product(self, product, **kwargs):
        # Llama al método para registrar el producto visto
        request.env['product.view.history'].sudo().add_product_to_history(product.id)
        return request.render("website_sale.product", {'product': product})