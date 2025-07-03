import logging
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

_logger = logging.getLogger(__name__)

class WebsiteSaleExtended(WebsiteSale):
    
    @http.route(['/shop/cart'], type='http', auth="public", website=True)
    def cart(self, **post):
        response = super(WebsiteSaleExtended, self).cart(**post)
        if isinstance(response, dict):
            # Agregar elementos guardados al contexto
            response['saved_items'] = request.session.get('saved_items', [])
        return response
    
    @http.route(['/shop/cart/save_for_later'], type='http', auth="public", website=True)
    def save_for_later(self, line_id, product_id, **post):
        """Mover un producto del carrito a los guardados"""
        order = request.website.sale_get_order()
        if not order or not line_id or not product_id:
            return request.redirect("/shop/cart")
            
        line_id = int(line_id)
        product_id = int(product_id)
        
        # Buscar la línea de orden
        line = request.env['sale.order.line'].sudo().browse(line_id)
        if not line or line.order_id != order:
            return request.redirect("/shop/cart")
            
        # Guardar detalles del producto en la sesión antes de eliminar del carrito
        saved_items = request.session.get('saved_items', [])
        
        product = request.env['product.product'].sudo().browse(product_id)
        
        # Generar ID único para el elemento guardado
        item_id = 1
        if saved_items:
            existing_ids = [item.get('id', 0) for item in saved_items]
            item_id = max(existing_ids) + 1
            
        saved_item = {
            'id': item_id,  # Usar un ID generado más confiable
            'product_id': product.id,
            'name': product.display_name,
            'price': product.list_price,  # Simplificar para evitar errores de atributos
            'template_id': product.product_tmpl_id.id,
            'quantity_available': product.qty_available,
            'brand_id': product.product_tmpl_id.brand_type_id.id if hasattr(product.product_tmpl_id, 'brand_type_id') and product.product_tmpl_id.brand_type_id else '',
            'brand_name': product.product_tmpl_id.brand_type_id.name if hasattr(product.product_tmpl_id, 'brand_type_id') and product.product_tmpl_id.brand_type_id else '',
        }
        
        # Forzar actualización de la sesión
        saved_items.append(saved_item)
        request.session['saved_items'] = saved_items
        request.session.modified = True
        
        try:
            # Eliminar el elemento del carrito
            order._cart_update(product_id=product.id, line_id=line_id, add_qty=0)
        except Exception as e:
            _logger.error("Error al eliminar producto del carrito: %s", e)
        
        return request.redirect("/shop/cart")
        
    @http.route(['/shop/cart/move_to_cart'], type='http', auth="public", website=True)
    def move_to_cart(self, item_id, **post):
        """Mover un producto de guardados al carrito"""
        if not item_id:
            return request.redirect("/shop/cart")
            
        item_id = int(item_id)
        saved_items = request.session.get('saved_items', [])
        
        # Encontrar el elemento guardado
        item = None
        new_saved_items = []
        for saved_item in saved_items:
            if saved_item['id'] == item_id:
                item = saved_item
            else:
                new_saved_items.append(saved_item)
                
        if not item:
            return request.redirect("/shop/cart")
            
        # Añadir el producto al carrito
        product = request.env['product.product'].sudo().browse(item['product_id'])
        order = request.website.sale_get_order(force_create=1)
        order._cart_update(product_id=product.id, add_qty=1)
        
        # Actualizar la lista de elementos guardados
        request.session['saved_items'] = new_saved_items
        
        return request.redirect("/shop/cart")
        
    @http.route(['/shop/cart/remove_saved_item'], type='http', auth="public", website=True)
    def remove_saved_item(self, item_id, **post):
        """Eliminar un producto de guardados"""
        if not item_id:
            return request.redirect("/shop/cart")
            
        item_id = int(item_id)
        saved_items = request.session.get('saved_items', [])
        
        # Eliminar de elementos guardados
        request.session['saved_items'] = [i for i in saved_items if i['id'] != item_id]
        
        return request.redirect("/shop/cart")
    
    @http.route(['/debug/saved_items'], type='http', auth="public", website=True)
    def debug_saved_items(self, **post):
        """Debug para ver los elementos guardados en la sesión"""
        saved_items = request.session.get('saved_items', [])
        return request.make_response(f"<pre>Saved items: {saved_items}</pre>")