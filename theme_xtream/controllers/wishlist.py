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
        selected_ids = request.httprequest.form.getlist('wishlist_select')
        
        if selected_ids:
            # Convertir los IDs a enteros y eliminar los productos seleccionados
            wishlist_items = request.env['product.wishlist'].sudo().browse([int(item_id) for item_id in selected_ids])
            wishlist_items.unlink()
        
        return request.redirect('/shop/wishlist')
    
    @http.route('/shop/wishlist/remove/<int:item_id>', type='http', auth='public', methods=['POST'], website=True)
    def remove_wishlist_item(self, item_id):
        # Eliminar un producto específico de la wishlist
        wishlist_item = request.env['product.wishlist'].sudo().browse(item_id)
        if wishlist_item.exists():
            wishlist_item.unlink()
        return request.redirect('/shop/wishlist')
    

    @http.route('/shop/wishlist/toggle', type='json', auth='public', methods=['POST'], website=True)
    def toggle_wishlist(self, product_template_id=None, product_variant_id=None):
        if not product_template_id or not product_variant_id:
            return {'error': 'Missing parameters'}

        partner = request.env.user.partner_id
        if not partner:
            return {'error': 'User not logged in'}

        wishlist_model = request.env['product.wishlist'].sudo()
        existing_item = wishlist_model.search([
            ('partner_id', '=', partner.id),
            ('product_template_id', '=', int(product_template_id)),
            ('product_variant_id', '=', int(product_variant_id))
        ])

        if existing_item:
            existing_item.unlink()
            return {'added': False, 'message': 'Removed from wishlist'}
        else:
            wishlist_model.create({
                'partner_id': partner.id,
                'product_template_id': int(product_template_id),
                'product_variant_id': int(product_variant_id)
            })
            return {'added': True, 'message': 'Added to wishlist'}