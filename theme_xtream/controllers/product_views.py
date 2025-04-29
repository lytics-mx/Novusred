from odoo import http
from odoo.http import request

class ShopController(http.Controller):

    @http.route(['/tienda/product/<model("product.product"):product>'], type='http', auth="public", website=True)
    def product_page(self, product, **kwargs):
        # Renderiza la plantilla personalizada con el producto seleccionado
        return request.render("theme_xtream.custom_product_template", {'product': product})