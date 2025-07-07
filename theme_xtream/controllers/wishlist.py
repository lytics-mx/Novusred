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