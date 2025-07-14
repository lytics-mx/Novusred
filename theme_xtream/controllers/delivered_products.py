from odoo import http
from odoo.http import request
from babel.dates import format_date  # Importar babel para formatear fechas

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
                    'delivery_date': format_date(picking.date_done, format='d MMMM yyyy', locale='es') if picking.date_done else '',
                    'purchase_date': format_date(picking.date, format='d MMMM yyyy', locale='es') if picking.date else '',  # Formato de fecha en español
                    'image_url': f'/web/image/product.product/{move.product_id.id}/image_1920',
                    'state': picking.state,  # Agregar el estado del stock.picking
                    'picking_origin': picking.origin,  # Identificador del picking (origin)
                    'picking_name': picking.name,  # Nombre del picking
                })
        
        # Obtener todos los productos de los pickings pendientes
        pending_products = []
        for picking in pending_pickings:
            for move in picking.move_ids_without_package:
                pending_products.append({
                    'product_id': move.product_id.id,  # Agregar product_id
                    'product_name': move.product_id.name,
                    'quantity': move.product_qty,
                    'scheduled_date': format_date(picking.scheduled_date, format='d MMMM yyyy', locale='es') if picking.scheduled_date else '',
                    'purchase_date': format_date(picking.date, format='d MMMM yyyy', locale='es') if picking.date else '',  # Formato de fecha en español
                    'image_url': f'/web/image/product.product/{move.product_id.id}/image_1920',
                    'state': picking.state,  # Agregar el estado del stock.picking
                    'picking_origin': picking.origin,  # Identificador del picking (origin)
                    'picking_name': picking.name,  # Nombre del picking
                })
        
        return request.render('theme_xtream.delivered_template', {
            'delivered_products': delivered_products,
            'pending_products': pending_products,
        })