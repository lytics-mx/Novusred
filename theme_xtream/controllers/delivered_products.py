from odoo import http
from odoo.http import request
from babel.dates import format_date
from datetime import datetime, timedelta

class WebsiteCheckout(http.Controller):
    @http.route(['/delivered_products'], type='http', auth='user', website=True)
    def delivered_products(self, product_id, pick_origin):
        user = request.env.user

        # Diccionario de traducción de estados
        state_translation = {
            'waiting': 'Alistándose',
            'assigned': 'En camino',
            'done': 'Entregado'
        }

        # Buscar el producto por ID
        product = request.env['product.product'].sudo().browse(product_id)

        # Obtener la marca desde el modelo brand.type
        brand = product.product_tmpl_id.brand_type_id
        brand_name = brand.name if brand else 'Sin marca'
        brand_image_url = f'/web/image/brand.type/{brand.id}/icon_image' if brand else '/web/static/src/img/placeholder.png'

        # Buscar pickings relacionados con el producto, el usuario y el picking_origin
        pickings = request.env['stock.picking'].sudo().search([
            ('partner_id', '=', user.partner_id.id),
            ('move_ids_without_package.product_id', '=', product_id),
            ('origin', '=', pick_origin)  # Filtrar por picking_origin
        ], limit=1)  # Limitar a un registro para evitar múltiples resultados
        
        # Verificar si se encontró un picking
        if pickings:
            picking = pickings[0]  # Obtener el primer picking
            # Preparar detalles del envío
            shipping_details = {
                'partner_name': picking.partner_id.name if picking.partner_id else '',
                'partner_address': picking.partner_id.contact_address if picking.partner_id else '',
                'responsible': picking.user_id.name if picking.user_id else '',
                'carrier': picking.carrier_id.name if picking.carrier_id else '',
                'shipping_weight': picking.shipping_weight or 0.0,
            }
        else:
            # Si no hay pickings, inicializar shipping_details vacío
            shipping_details = {
                'partner_name': '',
                'partner_address': '',
                'responsible': '',
                'carrier': '',
                'shipping_weight': 0.0,
            }

        # Preparar datos del producto
        product_info = {
            'id': product.id,
            'template_id': product.product_tmpl_id.id,  # ID del product.template
            'name': product.name,
            'brand': brand_name,
            'brand_image_url': brand_image_url,
            'image_url': f'/web/image/product.product/{product.id}/image_1920',
            'free_shipping': product.product_tmpl_id.free_shipping,  # Agregar el atributo free_shipping

        }

        # Preparar detalles de la compra y seguimiento
        purchase_details = []
        tracking_states = ['waiting', 'assigned', 'done']  # Estados relevantes
        for picking in pickings:
            for move in picking.move_ids_without_package.filtered(lambda m: m.product_id.id == product_id):
                state = picking.state or 'waiting'
                state_index = tracking_states.index(state) if state in tracking_states else -1  # Validar estado

                # Calcular días restantes para la fecha límite
                date_deadline = picking.date_deadline
                days_remaining = ''
                if date_deadline:
                    today = datetime.today()
                    delta = (date_deadline - today).days
                    if state == 'done':
                        days_remaining = f"Entregado el día {format_date(picking.date_done, format='d MMMM', locale='es')}" if picking.date_done else "Entregado"
                    elif delta > 30:
                        days_remaining = format_date(date_deadline, format="d 'de' MMMM yyyy", locale='es')  # Mostrar fecha específica si es mayor a un mes
                    elif delta > 7:
                        days_remaining = format_date(date_deadline, format="d 'de' MMMM", locale='es')  # Mostrar fecha específica si es mayor a una semana
                    elif delta > 1:
                        days_remaining = f"Llega en {delta} días"
                    elif delta == 1:
                        days_remaining = "Llega mañana"
                    elif delta == 0:
                        days_remaining = "Llega hoy"
                    else:
                        days_remaining = "Fecha límite pasada"

                purchase_details.append({
                    'quantity': move.product_qty,
                    'purchase_date': format_date(picking.date, format="d 'de' MMMM", locale='es') if picking.date else '',
                    'delivery_date': picking.date_done,
                    'state': state,  # Estado actual del picking
                    'state_index': state_index,  # Índice del estado en tracking_states
                    'tracking_states': tracking_states,  # Posibles estados
                    'price': move.product_id.list_price,  # Precio del producto
                    'total': move.product_qty * move.product_id.list_price,  # Total calculado
                    'picking_origin': picking.origin,  # Identificador del picking (origin)
                    'picking_name': picking.name,  # Nombre del picking
                    'date_deadline': format_date(date_deadline, format="d 'de' MMMM", locale='es') if date_deadline else '',
                    'days_remaining': days_remaining,  # Texto del contador
                })

        return request.render('theme_xtream.delivered_template', {
            'product_info': product_info,
            'purchase_details': purchase_details,
            'state_translation': state_translation,  # Traducción de estados
            'shipping_details': shipping_details,

        })