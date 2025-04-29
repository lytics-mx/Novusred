from odoo import http
from odoo.http import request
import logging
_logger = logging.getLogger(__name__)
    
class ShopController(http.Controller):


    @http.route(['/tienda/producto/<model("product.product"):product>'], type='http', auth="public", website=True)
    def product_page(self, product, **kwargs):
        if not product:
            return request.not_found()  # Devuelve un error 404 si el producto no existe
        _logger.info("Producto cargado: %s", product)
        return request.render("theme_xtream.product_detail_template", {'product': product})