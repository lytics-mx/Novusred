from odoo import http
from odoo.http import request

class WishlistController(http.Controller):
    @http.route('/shop/wishlist', type='http', auth='public', website=True)
    def wishlist_page(self):
        # Obtener los productos favoritos del usuario actual
        partner = request.env.user.partner_id
        wishlist_items = request.env['product.wishlist'].sudo().search([('partner_id', '=', partner.id)])
        
        # Preparar los datos para el template
        items_data = []
        for item in wishlist_items:
            items_data.append({
                'name': item.product_id.name,
                'brand': item.product_id.brand_id.name if item.product_id.brand_id else '',
                'price': item.product_id.lst_price,
                'discount': f"{item.product_id.discount_percentage}% OFF" if item.product_id.discount_percentage else '',
                'shipping': 'Envío gratis' if item.product_id.free_shipping else '',
                'image_url': f'/web/image/product/{item.product_id.id}/image',
                'resolution': item.product_id.image_resolution if item.product_id.image_resolution else '',
            })
        
        return request.render('theme_xtream.wishlist_template', {'wishlist_items': items_data})