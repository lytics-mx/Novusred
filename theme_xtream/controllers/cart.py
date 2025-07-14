from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import http
from odoo.http import request
import time
import logging
_logger = logging.getLogger(__name__)


class ShopController(WebsiteSale):

    @http.route('/shop/cart', type='http', auth="public", website=True)
    def cart(self, tab=None, **kw):
        order = request.website.sale_get_order()
        saved_items = request.session.get('saved_for_later', [])
        values = {
            'website_sale_order': order,
            'saved_items': saved_items,
            'active_tab': tab or 'cart',
        }
        return request.render("theme_xtream.website_cart_buy_now", values)
    
    def _prepare_cart_values(self, **kwargs):
        values = super()._prepare_cart_values(**kwargs)
        values['saved_items'] = kwargs.get('saved_items', request.session.get('saved_for_later', []))
        return values


    @http.route('/shop/cart/remove', type='http', auth="public", website=True)
    def cart_remove(self, line_id=None, **kw):
        if line_id:
            order = request.website.sale_get_order()
            if order:
                line = order.order_line.filtered(lambda l: l.id == int(line_id))
                if line:
                    line.unlink()
        return request.redirect('/shop/cart')
    
    @http.route('/shop/cart/update_badge', type='json', auth="public", website=True)
    def update_cart_badge(self, total_items=None, **post):
        if total_items is not None:
            request.session['website_sale_cart_quantity'] = int(total_items)
            
            # También actualiza el contador en la orden actual
            order = request.website.sale_get_order(force_create=0)
            if order:
                # Recalcular la cantidad total de productos en la orden
                # (Esto es opcional, ya que la cantidad visual se actualizará con total_items)
                quantity = sum(line.product_uom_qty for line in order.order_line)
                if quantity != total_items:
                    # Solo registrar la diferencia, no es necesario hacer nada más
                    _logger.info(f"Diferencia entre cantidad visual ({total_items}) y real ({quantity})")
            
            return {'success': True, 'cart_quantity': total_items}
        return {'success': False}
       

       
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
                            'id': line.id,  # Usar el ID real de la línea
                            'product_id': product_id,
                            'template_id': line.product_id.product_tmpl_id.id,
                            'name': line.product_id.display_name,
                            'price': getattr(line.product_id, 'discounted_price', line.product_id.list_price),
                            'quantity': line.product_uom_qty,
                            'quantity_available': line.product_id.qty_available,
                        }
                        
                        if getattr(line.product_id.product_tmpl_id, 'brand_type_id', False):
                            product_data.update({
                                'brand_name': line.product_id.product_tmpl_id.brand_type_id.name,
                                'brand_id': line.product_id.product_tmpl_id.brand_type_id.id,
                            })
                        
                        # Guardar el producto en la pestaña "Guardados"
                        saved_items = request.session.get('saved_for_later', [])
                        saved_items.append(product_data)
                        request.session['saved_for_later'] = saved_items
                        request.session.modified = True
                        
                        # Marcar la línea como "guardada" (sin eliminarla)
                        line.write({'product_uom_qty': 0})  # Ajustar cantidad a 0 para ocultarla del carrito
        except Exception as e:
            _logger.error(f"Error al guardar producto para después: {str(e)}", exc_info=True)
            
        return request.redirect('/shop/cart?tab=saved')
    
    @http.route('/shop/cart/remove_saved_item', type='http', auth="public", website=True)
    def remove_saved_item(self, item_id=None, **kw):
        if item_id:
            item_id = int(item_id)
            saved_items = request.session.get('saved_for_later', [])
            request.session['saved_for_later'] = [item for item in saved_items if item['id'] != item_id]
            request.session.modified = True
        return request.redirect('/shop/cart?tab=saved')

    
    @http.route('/shop/cart/move_to_cart', type='http', auth="public", website=True)
    def move_to_cart(self, item_id=None, **kw):
        if item_id:
            item_id = int(item_id)
            saved_items = request.session.get('saved_for_later', [])
            item_to_move = None
            new_saved_items = []
            
            for item in saved_items:
                if item['id'] == item_id:
                    item_to_move = item
                else:
                    new_saved_items.append(item)
                    
            if item_to_move:
                request.session['saved_for_later'] = new_saved_items
                request.session.modified = True
                
                # Añadir al carrito
                order = request.website.sale_get_order(force_create=1)
                order._cart_update(product_id=item_to_move['product_id'], add_qty=1)
                
        return request.redirect('/shop/cart')    
    
    @http.route('/shop/cart/update_bundle', type='http', auth="public", website=True)
    def update_bundle_cart(self, **post):
        """
        Handle adding multiple products (bundle) to the cart.
        """
        # Obtener los IDs de los productos seleccionados como una lista
        bundle_product_ids = request.httprequest.form.getlist('bundle_product_ids[]')  # Manejo correcto de múltiples valores
        root_product_id = post.get('product_id')
        add_qty = int(post.get('add_qty', 1))  # Default quantity is 1
    
        if root_product_id:
            bundle_product_ids.append(root_product_id)
    
        if bundle_product_ids:
            order = request.website.sale_get_order(force_create=1)
            for product_id in bundle_product_ids:
                try:
                    product_id = int(product_id)
                    order._cart_update(product_id=product_id, add_qty=add_qty)
                except ValueError:
                    _logger.error(f"Error al procesar el producto ID: {product_id}")
                    continue
    
        _logger.info(f"Productos añadidos al carrito: {bundle_product_ids}")
        return request.redirect('/shop/cart')