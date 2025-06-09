from odoo.addons.website.controllers.main import Website
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from werkzeug.utils import redirect
import logging
_logger = logging.getLogger(__name__)

class ShopController(WebsiteSale):

    @http.route([
        '/view/<model("product.template"):product>',
        '/view/product/<model("product.template"):product>'
    ], type='http', auth="public", website=True, csrf=False)  # <--- csrf desactivado
    def product_page(self, product, **kwargs):
        # ...existing code...
        if not product:
            return request.not_found()
        _logger.info("Producto cargado: %s", product)

        # Obtener la jerarquía de categorías
        categories = []
        categ = product.categ_id
        while categ:
            categories.insert(0, categ)
            categ = categ.parent_id

        # Obtener la URL de referencia (página anterior)
        referer = request.httprequest.headers.get('Referer', '/')
        # Cálculo de descuentos (ejemplo)
        discounted_price = product.list_price
        discount_percentage = 0
        fixed_discount = 0
        if hasattr(product, 'discounted_price'):
            discounted_price = product.discounted_price
        elif hasattr(product, 'standard_price') and product.list_price > product.standard_price:
            discounted_price = product.standard_price
        if product.list_price > discounted_price:
            fixed_discount = product.list_price - discounted_price
            discount_percentage = int(100 * fixed_discount / product.list_price)

        context = {
            'product': product,
            'categories': categories,
            'referer': referer,
            'discounted_price': discounted_price,
            'discount_percentage': discount_percentage,
            'fixed_discount': fixed_discount,
        }
        return request.render("theme_xtream.website_view_product_xtream", context)
    
    @http.route('/shop/cart', type='http', auth="public", methods=['POST'], website=True, csrf=True)
    def cart_update(self, product_id, add_qty=1, **post):
        # Usar el método original de WebsiteSale para agregar producto al carrito
        response = super(ShopController, self).cart_update(product_id=product_id, add_qty=add_qty, **post)
        # Redirigir a la página del carrito después de agregar el producto
        return redirect('/shop/cart')