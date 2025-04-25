from odoo import http
from odoo.http import request

class ShopController(http.Controller):

    @http.route(['/shop/product/<model("product.template"):product>'], type='http', auth="public", website=True)
    def product_page(self, product, **kwargs):
        # Registrar el producto visitado
        if request.env.user.partner_id:
            visitor = request.env['website.visitor']._get_visitor_from_request()
            if visitor:
                request.env['website.track'].sudo().create({
                    'visitor_id': visitor.id,
                    'product_id': product.id,
                })
        # Renderizar la página del producto
        return request.render("website_sale.product", {'product': product})