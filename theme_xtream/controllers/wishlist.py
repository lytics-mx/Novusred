from odoo import http
from odoo.http import request

class WishlistController(http.Controller):
    @http.route('/shop/wishlist', type='http', auth='public', website=True)
    def wishlist_page(self):
        # Obtener los productos de la wishlist del usuario actual
        wishlist_items = request.env['product.wishlist'].sudo().search([('partner_id', '=', request.env.user.partner_id.id)])
        
        # Pasar los productos y el token CSRF al contexto de la plantilla
        context = {
            'wishlist_items': wishlist_items,
            'csrf_token': request.csrf_token(),
        }
        return request.render('theme_xtream.wishlist_template', context)

    @http.route('/shop/wishlist/clear', type='http', auth='public', methods=['POST'], website=True)
    def clear_wishlist(self):
        # Obtener los IDs de los productos seleccionados desde el formulario
        selected_ids = request.httprequest.form.getlist('wishlist_select[]')  # Asegúrate de usar el nombre correcto
        
        if selected_ids:
            # Convertir los IDs a enteros y eliminar los productos seleccionados
            selected_ids = list(map(int, selected_ids))  # Convertir a enteros
            wishlist_items = request.env['product.wishlist'].sudo().browse(selected_ids)
            if wishlist_items:
                wishlist_items.unlink()  # Eliminar todos los productos seleccionados de una sola vez
        
        return request.redirect('/shop/wishlist')
    
    @http.route('/shop/wishlist/remove/<int:item_id>', type='http', auth='public', methods=['POST'], website=True)
    def remove_wishlist_item(self, item_id):
        wishlist_item = request.env['product.wishlist'].sudo().browse(item_id)
        if wishlist_item.exists():
            wishlist_item.unlink()
        return request.redirect('/shop/wishlist')

    @http.route('/shop/wishlist/add', type='http', auth='public', methods=['POST'], website=True)
    def add_to_wishlist(self):
        product_id = int(request.httprequest.form.get('product_id', 0))
        if product_id and request.env.user.partner_id:
            request.env['product.wishlist'].sudo().create({
                'product_id': product_id,
                'partner_id': request.env.user.partner_id.id,
            })
        return request.redirect('/shop/wishlist')
