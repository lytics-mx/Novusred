from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import http
from odoo.http import request

class ShopController(WebsiteSale):

    @http.route('/shop/cart', type='http', auth="public", website=True)
    def cart(self, **post):
        buy_now = post.get('buy_now') or request.httprequest.args.get('buy_now')
        values = {}
        
        # Añadir saved_items a los valores
        values['saved_items'] = request.session.get('saved_for_later', [])
        
        if buy_now:
            return request.render('theme_xtream.website_cart_buy_now', self._prepare_cart_values(**values))
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
    
    @http.route('/shop/cart/update_badge', type='json', auth="public", website=True)
    def update_cart_badge(self, total_items=None, **post):
        if total_items is not None:
            request.session['website_sale_cart_quantity'] = int(total_items)
            return {'success': True}
        return {'success': False}
    
    @http.route('/shop/cart/save_for_later', type='http', auth="public", website=True)
    def cart_save_for_later(self, line_id=None, product_id=None, **kw):
        if line_id and product_id:
            order = request.website.sale_get_order()
            if order:
                line = order.order_line.filtered(lambda l: l.id == int(line_id))
                if line:
                    # Guardar información del producto antes de eliminar la línea
                    product_data = {
                        'id': int(time.time()),  # ID temporal único
                        'product_id': int(product_id),
                        'template_id': line.product_id.product_tmpl_id.id,
                        'name': line.product_id.display_name,
                        'price': line.product_id.discounted_price or line.product_id.list_price,
                        'quantity_available': line.product_id.qty_available,
                    }
                    
                    if line.product_id.product_tmpl_id.brand_type_id:
                        product_data.update({
                            'brand_name': line.product_id.product_tmpl_id.brand_type_id.name,
                            'brand_id': line.product_id.product_tmpl_id.brand_type_id.id,
                        })
                    
                    # Añadir a la lista de guardados en la sesión
                    saved_items = request.session.get('saved_for_later', [])
                    saved_items.append(product_data)
                    request.session['saved_for_later'] = saved_items
                    
                    # Eliminar la línea del carrito
                    line.unlink()
                    
        return request.redirect('/shop/cart')  
    
    @http.route('/shop/cart/remove_saved_item', type='http', auth="public", website=True)
    def remove_saved_item(self, item_id=None, **kw):
        if item_id:
            saved_items = request.session.get('saved_for_later', [])
            request.session['saved_for_later'] = [item for item in saved_items if item['id'] != int(item_id)]
        return request.redirect('/shop/cart')

    
    @http.route('/shop/cart/move_to_cart', type='http', auth="public", website=True)
    def move_to_cart(self, item_id=None, **kw):
        if item_id:
            saved_items = request.session.get('saved_for_later', [])
            item_to_move = None
            
            # Encontrar y eliminar el item de la lista de guardados
            new_saved_items = []
            for item in saved_items:
                if item['id'] == int(item_id):
                    item_to_move = item
                else:
                    new_saved_items.append(item)
            
            if item_to_move:
                request.session['saved_for_later'] = new_saved_items
                
                # Añadir al carrito
                product = request.env['product.product'].sudo().browse(item_to_move['product_id'])
                if product:
                    request.website.sale_get_order(force_create=1)._cart_update(
                        product_id=int(item_to_move['product_id']),
                        add_qty=1
                    )
        
        return request.redirect('/shop/cart')        