from odoo import http
from odoo.http import request
from babel.dates import format_date
from datetime import datetime

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
                date_deadline = picking.date_deadline
                delivery_date = ''
                if date_deadline:
                    today = datetime.today()
                    delta = (date_deadline - today).days
                    if picking.state == 'done':
                        delivery_date = f"Entregado el día {format_date(picking.date_done, format='d MMMM', locale='es')}" if picking.date_done else "Entregado"
                    elif delta > 30:
                        delivery_date = format_date(date_deadline, format="d 'de' MMMM yyyy", locale='es')
                    elif delta > 7:
                        delivery_date = format_date(date_deadline, format="d 'de' MMMM", locale='es')
                    elif delta > 1:
                        delivery_date = f"Llega en {delta} días"
                    elif delta == 1:
                        delivery_date = "Llega mañana"
                    elif delta == 0:
                        delivery_date = "Llega hoy"
                    else:
                        delivery_date = "Fecha límite pasada"

                purchase_date = ''
                if picking.date:
                    purchase_date = format_date(picking.date, format='d \'de\' MMMM', locale='es')

                delivered_products.append({
                    'product_id': move.product_id.id,
                    'product_name': move.product_id.name,
                    'quantity': move.product_qty,
                    'delivery_date': delivery_date,  # Usar la nueva lógica
                    'purchase_date': purchase_date,
                    'image_url': f'/web/image/product.product/{move.product_id.id}/image_1920',
                    'state': picking.state,
                    'picking_origin': picking.origin,
                    'picking_name': picking.name,
                })
        
        # Obtener todos los productos de los pickings pendientes
        pending_products = []
        for picking in pending_pickings:
            for move in picking.move_ids_without_package:
                scheduled_date = ''
                if picking.scheduled_date:
                    scheduled_date = format_date(picking.scheduled_date, format='d \'de\' MMMM', locale='es')

                purchase_date = ''
                if picking.date:
                    purchase_date = format_date(picking.date, format='d \'de\' MMMM', locale='es')

                pending_products.append({
                    'product_id': move.product_id.id,
                    'product_name': move.product_id.name,
                    'quantity': move.product_qty,
                    'scheduled_date': scheduled_date,
                    'purchase_date': purchase_date,
                    'image_url': f'/web/image/product.product/{move.product_id.id}/image_1920',
                    'state': picking.state,
                    'picking_origin': picking.origin,
                    'picking_name': picking.name,
                })
        
        return request.render('theme_xtream.delivered_template', {
            'delivered_products': delivered_products,
            'pending_products': pending_products,
        })