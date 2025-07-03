from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import http
from odoo.http import request

class ShopController(WebsiteSale):

    @http.route('/shop/cart', type='http', auth="public", website=True)
    def cart(self, **post):
        buy_now = post.get('buy_now') or request.httprequest.args.get('buy_now')
        order = request.website.sale_get_order()

        # Obtener productos relacionados basados en la marca del primer producto en el carrito
        related_products = []
        if order and order.order_line:
            first_product = order.order_line[0].product_id.product_tmpl_id
            if first_product.brand_type_id:
                related_products = request.env['product.template'].sudo().search([
                    ('brand_type_id', '=', first_product.brand_type_id.id),
                    ('website_published', '=', True),
                    ('id', 'not in', order.order_line.mapped('product_id.product_tmpl_id.id'))
                ], limit=12)

        # Preparar valores del carrito
        cart_values = self._prepare_cart_values()
        cart_values.update({
            'related_products': related_products,
        })

        if buy_now:
            # Renderiza tu nueva plantilla personalizada
            return request.render('theme_xtream.website_cart_buy_now', cart_values)

        # Si no es compra directa, usa el comportamiento normal
        return super().cart(**post)