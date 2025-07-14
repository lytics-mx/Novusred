from odoo import http
from odoo.http import request
from babel.dates import format_date  # Importar babel para formatear fechas

class WebsiteCheckout(http.Controller):
    @http.route(['/delivered_products'], type='http', auth='user', website=True)
    def delivered_products(self):
        from datetime import datetime  # Importar datetime para obtener el año actual
        current_year = datetime.now().year  # Obtener el año actual

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
                delivery_date = ''
                if picking.date_done:
                    delivery_year = picking.date_done.year
                    delivery_date = format_date(picking.date_done, format='d MMMM', locale='es').capitalize()
                    if delivery_year != current_year:
                        delivery_date += f' {delivery_year}'  # Agregar el año si es diferente al actual

                purchase_date = ''
                if picking.date:
                    purchase_year = picking.date.year
                    purchase_date = format_date(picking.date, format='d MMMM', locale='es').capitalize()
                    if purchase_year != current_year:
                        purchase_date += f' {purchase_year}'  # Agregar el año si es diferente al actual

                delivered_products.append({
                    'product_id': move.product_id.id,  # Agregar product_id
                    'product_name': move.product_id.name,
                    'quantity': move.product_qty,
                    'delivery_date': delivery_date,
                    'purchase_date': purchase_date,
                    'image_url': f'/web/image/product.product/{move.product_id.id}/image_1920',
                    'state': picking.state,  # Agregar el estado del stock.picking
                    'picking_origin': picking.origin,  # Identificador del picking (origin)
                    'picking_name': picking.name,  # Nombre del picking
                })
        
        # Obtener todos los productos de los pickings pendientes
        pending_products = []
        for picking in pending_pickings:
            for move in picking.move_ids_without_package:
                scheduled_date = ''
                if picking.scheduled_date:
                    scheduled_year = picking.scheduled_date.year
                    scheduled_date = format_date(picking.scheduled_date, format='d MMMM', locale='es').capitalize()
                    if scheduled_year != current_year:
                        scheduled_date += f' {scheduled_year}'  # Agregar el año si es diferente al actual

                purchase_date = ''
                if picking.date:
                    purchase_year = picking.date.year
                    purchase_date = format_date(picking.date, format='d MMMM', locale='es').capitalize()
                    if purchase_year != current_year:
                        purchase_date += f' {purchase_year}'  # Agregar el año si es diferente al actual

                pending_products.append({
                    'product_id': move.product_id.id,  # Agregar product_id
                    'product_name': move.product_id.name,
                    'quantity': move.product_qty,
                    'scheduled_date': scheduled_date,
                    'purchase_date': purchase_date,
                    'image_url': f'/web/image/product.product/{move.product_id.id}/image_1920',
                    'state': picking.state,  # Agregar el estado del stock.picking
                    'picking_origin': picking.origin,  # Identificador del picking (origin)
                    'picking_name': picking.name,  # Nombre del picking
                })
        
        return request.render('theme_xtream.delivered_template', {
            'delivered_products': delivered_products,
            'pending_products': pending_products,
        })