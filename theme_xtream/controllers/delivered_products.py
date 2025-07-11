from odoo import http
from odoo.http import request
from datetime import datetime, timedelta

class WebsiteCheckout(http.Controller):
    @http.route(['/delivered_products'], type='http', auth='user', website=True)
    def delivered_products(self, search='', filter_date=''):
        user = request.env.user

        # Filtrar por fecha
        today = datetime.today()
        domain = [('partner_id', '=', user.partner_id.id)]
        
        if filter_date == 'today':
            domain.append(('date_done', '>=', today.strftime('%Y-%m-%d 00:00:00')))
            domain.append(('date_done', '<=', today.strftime('%Y-%m-%d 23:59:59')))
        elif filter_date == 'yesterday':
            yesterday = today - timedelta(days=1)
            domain.append(('date_done', '>=', yesterday.strftime('%Y-%m-%d 00:00:00')))
            domain.append(('date_done', '<=', yesterday.strftime('%Y-%m-%d 23:59:59')))
        elif filter_date.startswith('month:'):
            month = int(filter_date.split(':')[1])
            domain.append(('date_done', '>=', today.replace(day=1, month=month).strftime('%Y-%m-01 00:00:00')))
            domain.append(('date_done', '<', today.replace(day=1, month=month + 1).strftime('%Y-%m-01 00:00:00')))
        elif filter_date.startswith('year:'):
            year = int(filter_date.split(':')[1])
            domain.append(('date_done', '>=', f'{year}-01-01 00:00:00'))
            domain.append(('date_done', '<=', f'{year}-12-31 23:59:59'))

        # Filtrar pickings completados y relacionados con el usuario actual
        delivered_pickings = request.env['stock.picking'].sudo().search(domain + [('state', '=', 'done')])
        pending_pickings = request.env['stock.picking'].sudo().search(domain + [('state', 'not in', ['done', 'cancel'])])

        # Obtener todos los productos de los pickings entregados
        delivered_products = []
        for picking in delivered_pickings:
            for move in picking.move_ids_without_package:
                if search.lower() in move.product_id.name.lower():
                    delivered_products.append({
                        'product_name': move.product_id.name,
                        'quantity': move.product_qty,
                        'delivery_date': picking.date_done or '',
                        'order_date': picking.date or '',
                        'purchase_count': move.product_uom_qty,  # Contador de productos
                        'image_url': f'/web/image/product.product/{move.product_id.id}/image_1920',
                    })

        # Obtener todos los productos de los pickings pendientes
        pending_products = []
        for picking in pending_pickings:
            for move in picking.move_ids_without_package:
                if search.lower() in move.product_id.name.lower():
                    pending_products.append({
                        'product_name': move.product_id.name,
                        'quantity': move.product_qty,
                        'scheduled_date': picking.scheduled_date or '',
                        'order_date': picking.date or '',
                        'purchase_count': move.product_uom_qty,  # Contador de productos
                        'image_url': f'/web/image/product.product/{move.product_id.id}/image_1920',
                    })

        return request.render('theme_xtream.delivered_template', {
            'delivered_products': delivered_products,
            'pending_products': pending_products,
            'search': search,
            'filter_date': filter_date,
        })