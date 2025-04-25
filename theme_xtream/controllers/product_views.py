from odoo import http
from odoo.http import request

class ShopController(http.Controller):

    @http.route(['/shop/product/<model("product.template"):product>'], type='http', auth="public", website=True)
    def product_page(self, product, **kwargs):
        """Registra el producto visitado y restablece el estado oculto si es necesario."""
        visitor = request.env['website.visitor']._get_visitor_from_request()
        if visitor:
            track_entry = request.env['website.track'].sudo().search([
                ('visitor_id', '=', visitor.id),
                ('product_id', '=', product.id)
            ], limit=1)
    
            if track_entry:
                # Si ya existe, restablecer el estado oculto
                track_entry.sudo().write({'hidden': False})
            else:
                # Crear un nuevo registro si no existe
                request.env['website.track'].sudo().create({
                    'visitor_id': visitor.id,
                    'product_id': product.id,
                })
    
        # Renderizar la página del producto
        return request.render("website_sale.product", {'product': product})