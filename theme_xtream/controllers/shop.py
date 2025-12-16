from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import http
from odoo.http import request

class ShopController(WebsiteSale):

    @http.route('/shop/cart', type='http', auth="public", website=True)
    def cart(self, **post):
        buy_now = post.get('buy_now') or request.httprequest.args.get('buy_now')
        if buy_now:
            # Renderiza tu nueva plantilla personalizada
            return request.render('theme_xtream.website_cart_buy_now', self._prepare_cart_values())
        # Si no es compra directa, usa el comportamiento normal
        return super().cart(**post)
    
    