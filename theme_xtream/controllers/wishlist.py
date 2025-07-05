from odoo import http
from odoo.http import request

class WishlistController(http.Controller):
    @http.route('/shop/wishlist', type='http', auth='public', website=True)
    def wishlist_page(self):
        # Obtener los productos del wishlist del usuario actual
        user_id = request.env.user.id
        wishlist_items = request.env['product.wishlist'].sudo().search([('create_uid', '=', user_id)])
        
        # Preparar los productos para el template
        products = wishlist_items.mapped('product_id')
        
        # Renderizar el template con los productos del wishlist
        return request.render('theme_xtream.wishlist_template', {'products': products})