from odoo.addons.website.controllers.main import Website
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

        # Obtener la jerarquía de categorías
        categories = []
        categ = product.categ_id
        while categ:
            categories.insert(0, categ)
            categ = categ.parent_id

        context = {
            'product': product,
            'categories': categories,  # Lista ordenada desde raíz hasta la hoja
        }
        return request.render("theme_xtream.website_view_product_xtream", context)