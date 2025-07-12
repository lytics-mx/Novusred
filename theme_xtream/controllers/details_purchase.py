from odoo import http
from odoo.http import request

class ProductDetails(http.Controller):
    @http.route(['/product_details/<int:product_id>'], type='http', auth='user', website=True)
    def product_details(self, product_id):
        user = request.env.user

        # Buscar el producto por ID
        product = request.env['product.product'].sudo().browse(product_id)

        # Buscar pickings relacionados con el producto y el usuario
        pickings = request.env['stock.picking'].sudo().search([
            ('partner_id', '=', user.partner_id.id),
            ('move_ids_without_package.product_id', '=', product_id)
        ])

        # Preparar datos para el template
        product_info = {
            'name': product.name,
            'image_url': f'/web/image/product.product/{product.id}/image_1920',
        }

        purchase_details = []
        for picking in pickings:
            for move in picking.move_ids_without_package.filtered(lambda m: m.product_id.id == product_id):
                purchase_details.append({
                    'quantity': move.product_qty,
                    'purchase_date': picking.date.strftime('%d de %B') if picking.date else '',
                    'delivery_date': picking.date_done,
                    'state': picking.state,
                })

        return request.render('theme_xtream.product_details_template', {
            'product_info': product_info,
            'purchase_details': purchase_details,
        })