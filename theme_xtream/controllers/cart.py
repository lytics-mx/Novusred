from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class ShopController(WebsiteSale):

    @http.route('/shop/cart', type='http', auth="public", website=True)
    def cart(self, **kw):
        order = request.website.sale_get_order()
        values = {
            'website_sale_order': order,
        }
        return request.render("theme_xtream.website_cart", values)

    @http.route('/shop/saved_items', type='http', auth="public", website=True)
    def saved_items(self, **kw):
        saved_items = request.session.get('saved_for_later', [])
        values = {
            'saved_items': saved_items,
        }
        return request.render("theme_xtream.website_saved_items", values)

    @http.route(['/shop/cart/save_for_later'], type='http', auth="public", website=True)
    def save_for_later(self, line_id=None, product_id=None, **kwargs):
        try:
            if line_id and product_id:
                order = request.website.sale_get_order()
                if order:
                    line_id = int(line_id)
                    product_id = int(product_id)
                    
                    # Filtrar la línea del carrito
                    line = order.order_line.filtered(lambda l: l.id == line_id)
                    if line:
                        # Guardar información del producto en la sesión
                        product_data = {
                            'id': line.id,
                            'product_id': product_id,
                            'name': line.product_id.display_name,
                            'price': getattr(line.product_id, 'discounted_price', line.product_id.list_price),
                            'quantity': line.product_uom_qty,
                        }
                        
                        # Guardar el producto en la pestaña "Guardados"
                        saved_items = request.session.get('saved_for_later', [])
                        if not any(item['id'] == line.id for item in saved_items):
                            saved_items.append(product_data)
                        request.session['saved_for_later'] = saved_items
                        request.session.modified = True
                        
                        # Reducir la cantidad del producto en el carrito a 0
                        line.write({'product_uom_qty': 0})
                        
                        _logger.info(f"Producto guardado para después: {product_data}")
        except Exception as e:
            _logger.error(f"Error al guardar producto para después: {str(e)}", exc_info=True)
            
        return request.redirect('/shop/saved_items')