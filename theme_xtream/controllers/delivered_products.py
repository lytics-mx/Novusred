from odoo import http
from odoo.http import request

class WebsiteCheckout(http.Controller):
    @http.route(['/delivered_products'], type='http', auth='user', website=True)
    def delivered_products(self):
        user = request.env.user
        # Filtrar pickings completados y relacionados con el usuario actual
        delivered_pickings = request.env['stock.picking'].sudo().search([
            ('state', '=', 'done'),
            ('partner_id', '=', user.partner_id.id)
        ])
        # Filtrar pickings pendientes y relacionados con el usuario actual
        pending_pickings = request.env['stock.picking'].sudo().search([
            ('state', 'not in', ['done', 'cancel']),
            ('partner_id', '=', user.partner_id.id)
        ])
        
        # Obtener todos los productos de los pickings entregados
        delivered_products = []
        for picking in delivered_pickings:
            for move in picking.move_ids_without_package:
                delivered_products.append({
                    'product_id': move.product_id.id,  # Agregar product_id
                    'product_name': move.product_id.name,
                    'quantity': move.product_qty,
                    'delivery_date': picking.date_done,
                    'purchase_date': picking.date.strftime('%d de %B') if picking.date else '',  # Formato de fecha
                    'image_url': f'/web/image/product.product/{move.product_id.id}/image_1920',
                    'state': picking.state,  # Agregar el estado del stock.picking
                })
        
        # Obtener todos los productos de los pickings pendientes
        pending_products = []
        for picking in pending_pickings:
            for move in picking.move_ids_without_package:
                pending_products.append({
                    'product_id': move.product_id.id,  # Agregar product_id
                    'product_name': move.product_id.name,
                    'quantity': move.product_qty,
                    'scheduled_date': picking.scheduled_date,
                    'purchase_date': picking.date.strftime('%d de %B') if picking.date else '',  # Formato de fecha
                    'image_url': f'/web/image/product.product/{move.product_id.id}/image_1920',
                    'state': picking.state,  # Agregar el estado del stock.picking
                })
        
        return request.render('theme_xtream.delivered_template', {
            'delivered_products': delivered_products,
            'pending_products': pending_products,
        })