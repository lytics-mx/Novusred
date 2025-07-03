from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import http
from odoo.http import request

class ShopController(WebsiteSale):

    def _prepare_cart_values(self):
        """Prepara los valores del carrito para la plantilla."""
        order = request.website.sale_get_order()
        return {
            'website_sale_order': order,
            'order_lines': order.order_line if order else [],
        }

    @http.route('/shop/cart', type='http', auth="public", website=True)
    def cart(self, **post):
        buy_now = post.get('buy_now') or request.httprequest.args.get('buy_now')
        order = request.website.sale_get_order()

        # Obtener productos accesorios de los productos en el carrito
        accessory_products = []
        if order and order.order_line:
            accessory_ids = set()
            main_product_ids = set(order.order_line.mapped('product_id.product_tmpl_id.id'))
            for line in order.order_line:
                product = line.product_id.product_tmpl_id
                for acc in product.accessory_product_ids:
                    if acc.id not in main_product_ids and acc.id not in accessory_ids:
                        accessory_products.append(acc)
                        accessory_ids.add(acc.id)

        # Manejar productos seleccionados desde la vista de productos
        selected_product_ids = post.getlist('bundle_product_ids[]')
        if selected_product_ids:
            for product_id in selected_product_ids:
                product = request.env['product.product'].sudo().browse(int(product_id))
                if product.exists():
                    order._cart_update(
                        product_id=product.id,
                        add_qty=1,  # Ajusta la cantidad según sea necesario
                    )

        # Preparar valores del carrito
        cart_values = self._prepare_cart_values()
        cart_values.update({
            'accessory_products': accessory_products,
        })

        if buy_now:
            return request.render('theme_xtream.website_cart_buy_now', cart_values)

        return super(ShopController, self).cart(**post)