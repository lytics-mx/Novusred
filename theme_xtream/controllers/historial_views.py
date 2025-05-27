from odoo import http
from odoo.http import request
from collections import defaultdict
from datetime import datetime, timedelta
import pytz

class ProductHistoryController(http.Controller):

    @http.route('/shop/history', type='http', auth='user', website=True)
    def view_history(self):
        """Obtiene el historial de productos vistos por el usuario actual agrupado por períodos."""
        user_partner_id = request.env.user.partner_id.id
        
        # Obtener todas las visitas del usuario
        tracks = request.env['website.track'].sudo().search([
            ('visitor_id.partner_id', '=', user_partner_id),
            ('product_id', '!=', False)
        ], order='visit_datetime desc')
        
        # Configurar zona horaria
        user_tz = pytz.timezone('America/Mexico_City')
        now = datetime.now(user_tz)
        today = now.date()
        yesterday = today - timedelta(days=1)
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)
        
        # Agrupar por períodos
        grouped_history = {
            'Hoy': [],
            'Ayer': [],
            'Esta semana': [],
            'Este mes': [],
            'Anteriores': []
        }
        
        seen_products = set()  # Para evitar duplicados
        
        for track in tracks:
            # Convertir fecha a zona horaria del usuario
            if track.visit_datetime:
                visit_date = track.visit_datetime.astimezone(user_tz).date()
                product = track.product_id.product_tmpl_id
                
                # Evitar productos duplicados
                if product.id in seen_products or not product.website_published:
                    continue
                    
                seen_products.add(product.id)
                
                # Clasificar por período
                if visit_date == today:
                    grouped_history['Hoy'].append({
                        'product': product,
                        'visit_datetime': track.visit_datetime,
                        'track_id': track.id
                    })
                elif visit_date == yesterday:
                    grouped_history['Ayer'].append({
                        'product': product,
                        'visit_datetime': track.visit_datetime,
                        'track_id': track.id
                    })
                elif visit_date >= week_start and visit_date < yesterday:
                    grouped_history['Esta semana'].append({
                        'product': product,
                        'visit_datetime': track.visit_datetime,
                        'track_id': track.id
                    })
                elif visit_date >= month_start and visit_date < week_start:
                    grouped_history['Este mes'].append({
                        'product': product,
                        'visit_datetime': track.visit_datetime,
                        'track_id': track.id
                    })
                else:
                    # Más de un mes
                    month_name = visit_date.strftime('%B %Y')
                    if month_name not in grouped_history:
                        grouped_history[month_name] = []
                    grouped_history[month_name].append({
                        'product': product,
                        'visit_datetime': track.visit_datetime,
                        'track_id': track.id
                    })
        
        # Filtrar períodos vacíos
        filtered_history = {k: v for k, v in grouped_history.items() if v}
        
        return request.render('theme_xtream.history_template', {
            'grouped_history': filtered_history,
        })

    @http.route('/shop/history/remove/<int:product_id>', type='http', auth='user', website=True)
    def remove_from_history(self, product_id):
        """Elimina un producto del historial del usuario actual."""
        user_partner_id = request.env.user.partner_id.id
        
        # Buscar todos los registros de este producto para este usuario
        track_entries = request.env['website.track'].sudo().search([
            ('visitor_id.partner_id', '=', user_partner_id),
            ('product_id.product_tmpl_id', '=', product_id)
        ])

        # Eliminar todos los registros
        if track_entries:
            track_entries.unlink()

        # Redirigir de vuelta al historial
        return request.redirect('/shop/history')