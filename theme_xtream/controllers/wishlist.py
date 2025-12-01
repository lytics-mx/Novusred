from odoo import http
from odoo.http import request

class WishlistController(http.Controller):
    @http.route('/wishlist', type='http', auth='public', website=True)
    def wishlist_page(self):
        # Obtener los productos de la wishlist del usuario actual
        wishlist_items = request.env['product.wishlist'].sudo().search([('partner_id', '=', request.env.user.partner_id.id)])
        
        # Pasar los productos y el token CSRF al contexto de la plantilla
        context = {
            'wishlist_items': wishlist_items,
            'csrf_token': request.csrf_token(),
        }
        return request.render('theme_xtream.wishlist_template', context)

    @http.route('/wishlist/clear', type='http', auth='public', methods=['POST'], website=True)
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
    
    @http.route('/wishlist/add/<int:item_id>', type='http', auth='public', methods=['POST'], website=True)
    def add_wishlist_item(self, item_id):
        partner = request.env.user.partner_id
        if partner:
            # Evita duplicados
            exists = request.env['product.wishlist'].sudo().search([
                ('partner_id', '=', partner.id),
                ('product_id', '=', item_id)
            ], limit=1)
            if not exists:
                request.env['product.wishlist'].sudo().create({
                    'partner_id': partner.id,
                    'product_id': item_id
                })
        return request.redirect('/shop/wishlist')

