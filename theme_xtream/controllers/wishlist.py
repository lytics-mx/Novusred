from odoo import http
from odoo.http import request

class WishlistController(http.Controller):
    @http.route('/shop/wishlist', type='http', auth='public', website=True)
    def wishlist_page(self):
        # Obtener los productos de la wishlist del usuario actual
        wishlist_items = request.env['product.wishlist'].sudo().search([('partner_id', '=', request.env.user.partner_id.id)])
        
        # Pasar los productos al contexto de la plantilla
        context = {
            'wishlist_items': wishlist_items,
        }
        return request.render('theme_xtream.wishlist_template', context)

    @http.route('/shop/wishlist/clear', type='http', auth='public', methods=['POST'], website=True)
    def clear_wishlist(self):
        # Eliminar todos los productos de la wishlist del usuario actual
        wishlist_items = request.env['product.wishlist'].sudo().search([('partner_id', '=', request.env.user.partner_id.id)])
        wishlist_items.unlink()
        return request.redirect('/shop/wishlist')
    
    @http.route('/shop/wishlist/remove/<int:item_id>', type='http', auth='public', methods=['POST'], website=True)
    def remove_wishlist_item(self, item_id):
        # Eliminar un producto específico de la wishlist
        wishlist_item = request.env['product.wishlist'].sudo().browse(item_id)
        if wishlist_item.exists():
            wishlist_item.unlink()
        return request.redirect('/shop/wishlist')