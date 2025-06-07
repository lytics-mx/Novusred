from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class ShopController(http.Controller):

    @http.route([
        '/view/<model("product.template"):product>',
        '/view/product/<model("product.template"):product>'
    ], type='http', auth="public", website=True)
    def product_page(self, product, **kwargs):
        if not product:
            return request.not_found()
        _logger.info("Producto cargado: %s", product)
        return request.render("theme_xtream.website_view_product_xtream", {'product': product})