from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import http
from odoo.http import request

class ShopController(WebsiteSale):

    @http.route('/shop/cart', type='http', auth="public", website=True)
    def cart(self, **post):
        buy_now = post.get('buy_now') or request.httprequest.args.get('buy_now')
        if buy_now:
            return request.render('theme_xtream.website_cart_buy_now', self._prepare_cart_values())
        return super().cart(**post)

    @http.route('/shop/cart/remove', type='http', auth="public", website=True)
    def cart_remove(self, line_id=None, **kw):
        if line_id:
            order = request.website.sale_get_order()
            if order:
                line = order.order_line.filtered(lambda l: l.id == int(line_id))
                if line:
                    line.unlink()
        return request.redirect('/shop/cart')
    

    
    @http.route('/shop/cart/save_for_later', type='http', auth="public", website=True)
    def cart_save_for_later(self, line_id=None, product_id=None, **kw):
        if line_id:
            order = request.website.sale_get_order()
            if order:
                line = order.order_line.filtered(lambda l: l.id == int(line_id))
                if line:
                    # Aquí podrías guardar el producto en un historial personalizado
                    # Por ejemplo: request.env['your.history.model'].sudo().create({...})
                    line.unlink()
        return request.redirect('/shop/history')    