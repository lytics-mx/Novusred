from odoo import http
from odoo.http import request
from babel.dates import format_date
from datetime import datetime, timedelta

class WebsiteCheckout(http.Controller):
    @http.route(['/delivered_products'], type='http', auth='user', website=True)
    def delivered_products(self):
        today = datetime.now().date()  # Fecha actual
        user = request.env.user

        # Filtrar movimientos relacionados con el usuario actual
        stock_moves = request.env['stock.move'].sudo().search([
            ('partner_id', '=', user.partner_id.id)
        ])

        # Clasificar productos entregados y pendientes
        delivered_products = []
        pending_products = []

        for move in stock_moves:
            deadline_date = move.date_deadline.date() if move.date_deadline else None
            delivery_date = move.date.date() if move.date else None

            # Determinar el estado del producto
            if move.state == 'done':  # Entregado
                relative_date = format_date(delivery_date, format='d \'de\' MMMM', locale='es') if delivery_date else ''
                delivered_products.append({
                    'product_id': move.product_id.id,
                    'product_name': move.product_id.name,
                    'quantity': move.product_qty,
                    'delivery_date': relative_date,
                    'image_url': f'/web/image/product.product/{move.product_id.id}/image_1920',
                    'state': move.state,
                    'picking_origin': move.picking_id.origin,
                    'picking_name': move.picking_id.name,
                })
            else:  # Pendiente
                if deadline_date:
                    # Calcular la fecha relativa
                    days_diff = (deadline_date - today).days
                    if days_diff > 30:
                        relative_date = format_date(deadline_date, format='d \'de\' MMMM', locale='es')
                    elif days_diff > 7:
                        relative_date = 'dentro de una semana'
                    elif days_diff == 1:
                        relative_date = 'mañana'
                    elif days_diff == 0:
                        relative_date = 'hoy'
                    elif days_diff < 0:
                        relative_date = 'atrasado'
                    else:
                        relative_date = f'en {days_diff} días'
                else:
                    relative_date = 'Sin fecha límite'

                pending_products.append({
                    'product_id': move.product_id.id,
                    'product_name': move.product_id.name,
                    'quantity': move.product_qty,
                    'deadline_date': relative_date,
                    'image_url': f'/web/image/product.product/{move.product_id.id}/image_1920',
                    'state': move.state,
                    'picking_origin': move.picking_id.origin,
                    'picking_name': move.picking_id.name,
                })

        return request.render('theme_xtream.delivered_template', {
            'delivered_products': delivered_products,
            'pending_products': pending_products,
        })