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
        # Obtener los productos guardados para el usuario actual
        saved_items = request.env['saved.items'].sudo().search([('user_id', '=', request.env.user.id)])
        
        values = {
            'website_sale_order': order,
            'saved_items': saved_items,
            'active_tab': tab or 'cart',
        }
        return request.render("theme_xtream.website_cart_buy_now", values)

    def _prepare_cart_values(self, **kwargs):
        values = super()._prepare_cart_values(**kwargs)
        order = kwargs.get('order') or request.website.sale_get_order()
        saved_items = []
        if order:
            order_product_ids = set(line.product_id.id for line in order.order_line)
            session_saved_items = request.session.get('saved_for_later', [])
            saved_items = [
                item for item in session_saved_items
                if item.get('product_id') not in order_product_ids
            ]
        values['saved_items'] = saved_items
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
       
       

       
    @http.route('/shop/cart/move_to_saved', type='http', auth="public", website=True)
    def move_to_saved(self, line_id=None, **kw):
        if line_id:
            line_id = int(line_id)
            order = request.website.sale_get_order()
            if order:
                # Filtrar la línea del carrito
                line = order.order_line.filtered(lambda l: l.id == line_id)
                if line:
                    # Determinar el precio basado en etiquetas
                    price = line.product_id.discounted_price if line.product_id.discounted_price else line.product_id.list_price
    
                    # Guardar información del producto en el modelo
                    product_data = {
                        'user_id': request.env.user.id,
                        'product_id': line.product_id.id,
                        'name': line.product_id.display_name,
                        'price': price,
                        'quantity_available': line.product_id.qty_available,
                    }
    
                    # Agregar información de la marca si está disponible
                    if getattr(line.product_id.product_tmpl_id, 'brand_type_id', False):
                        product_data.update({
                            'brand_name': line.product_id.product_tmpl_id.brand_type_id.name,
                            'brand_id': line.product_id.product_tmpl_id.brand_type_id.id,
                        })
    
                    # Crear el registro en la base de datos
                    request.env['saved.items'].create(product_data)
    
                    # Eliminar la línea del carrito
                    line.unlink()
    
        return request.redirect('/shop/cart?tab=saved')
       
    @http.route('/shop/cart/remove_saved_item', type='http', auth="public", website=True)
    def remove_saved_item(self, item_id=None, **kw):
        if item_id:
            item_id = int(item_id)
            # Buscar el producto guardado en el modelo 'saved.items'
            saved_item = request.env['saved.items'].sudo().search([('id', '=', item_id), ('user_id', '=', request.env.user.id)])
            if saved_item:
                # Eliminar el producto guardado
                saved_item.unlink()
        return request.redirect('/shop/cart?tab=saved')

    
    @http.route('/shop/cart/move_to_cart', type='http', auth="public", website=True)
    def move_to_cart(self, item_id=None, **kw):
        if item_id:
            item_id = int(item_id)
            # Buscar el producto en "Guardados"
            saved_item = request.env['saved.items'].sudo().search([('id', '=', item_id), ('user_id', '=', request.env.user.id)])
            if saved_item:
                # Obtener el pedido actual
                order = request.website.sale_get_order(force_create=True)
                if order:
                    # Agregar el producto al carrito
                    request.env['sale.order.line'].sudo().create({
                        'order_id': order.id,
                        'product_id': saved_item.product_id.id,
                        'product_uom_qty': 1,  # Cantidad predeterminada
                        'price_unit': saved_item.price,
                    })
                    # Eliminar el producto de "Guardados"
                    saved_item.unlink()
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
    
    @http.route('/shop/cart/update', type='http', auth="public", website=True)
    def cart_update(self, line_id=None, set_qty=None, **kw):
        if line_id and set_qty:
            order = request.website.sale_get_order()
            if order:
                line = order.order_line.filtered(lambda l: l.id == int(line_id))
                if line:
                    try:
                        # Actualizar la cantidad del producto en el carrito
                        line.product_uom_qty = int(set_qty)
                    except ValueError:
                        _logger.error(f"Cantidad inválida: {set_qty}")
        return request.redirect('/shop/cart')