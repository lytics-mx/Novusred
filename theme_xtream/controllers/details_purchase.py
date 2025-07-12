from odoo import http
from odoo.http import request

class ProductDetails(http.Controller):
    @http.route(['/product_details/<int:product_id>'], type='http', auth='user', website=True)
    def product_details(self, product_id):
        user = request.env.user

        # Buscar el producto por ID
        product = request.env['product.product'].sudo().browse(product_id)

        # Obtener la marca desde el modelo brand.type
        brand = product.product_tmpl_id.brand_type_id
        brand_name = brand.name if brand else 'Sin marca'
        brand_image_url = f'/web/image/brand.type/{brand.id}/icon_image' if brand else '/web/static/src/img/placeholder.png'

        # Buscar pickings relacionados con el producto y el usuario
        pickings = request.env['stock.picking'].sudo().search([
            ('partner_id', '=', user.partner_id.id),
            ('move_ids_without_package.product_id', '=', product_id)
        ])

        # Preparar datos del producto
        product_info = {
            'name': product.name,
            'brand': brand_name,  # Nombre de la marca
            'brand_image_url': brand_image_url,  # URL de la imagen de la marca
            'image_url': f'/web/image/product.product/{product.id}/image_1920',
        }

        # Preparar detalles de la compra y seguimiento
        purchase_details = []
        tracking_states = ['draft', 'waiting', 'confirmed', 'assigned', 'done', 'cancel']
        for picking in pickings:
            for move in picking.move_ids_without_package.filtered(lambda m: m.product_id.id == product_id):
                state = picking.state or 'draft'
                state_index = tracking_states.index(state) if state in tracking_states else -1  # Validar estado

                purchase_details.append({
                    'quantity': move.product_qty,
                    'purchase_date': picking.date.strftime('%d de %B') if picking.date else '',
                    'delivery_date': picking.date_done,
                    'state': state,  # Estado actual del picking
                    'state_index': state_index,  # Índice del estado en tracking_states
                    'tracking_states': tracking_states,  # Posibles estados
                    'price': move.product_id.list_price,  # Precio del producto
                    'total': move.product_qty * move.product_id.list_price,  # Total calculado
                })

        return request.render('theme_xtream.product_details_template', {
            'product_info': product_info,
            'purchase_details': purchase_details,
        })