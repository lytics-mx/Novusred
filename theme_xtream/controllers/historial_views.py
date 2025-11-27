from odoo import http
from odoo.http import request
from collections import defaultdict
from datetime import datetime, timedelta
import pytz
import locale

class ProductHistoryController(http.Controller):

    def _get_month_name_spanish(self, date):
        """Convierte una fecha a nombre de mes en español."""
        months_spanish = {
            1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
            5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
            9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
        }
        return f"{months_spanish[date.month]} {date.year}"

    @http.route(['/shop/history', '/shop/history/<string:period_filter>'], type='http', auth='user', website=True)
    def view_history(self, period_filter=None):
        """Obtiene el historial de productos vistos por el usuario actual agrupado por períodos."""
        user_id = request.env.user.id
        

        # Buscar registros de website.track creados por nuestro beacon (tienen user_id)
        tracks = request.env['website.track'].search([
            ('user_id', '=', user_id),
            ('product_id', '!=', False),
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
        
        # Lista de todos los meses disponibles para el filtro
        available_periods = ['Hoy', 'Ayer', 'Esta semana', 'Este mes']
        month_periods = set()
        
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
                    # Más de un mes - usar nombres en español
                    month_name = self._get_month_name_spanish(visit_date)
                    month_periods.add(month_name)
                    if month_name not in grouped_history:
                        grouped_history[month_name] = []
                    grouped_history[month_name].append({
                        'product': product,
                        'visit_datetime': track.visit_datetime,
                        'track_id': track.id
                    })
        
        # Agregar meses disponibles a la lista de períodos
        available_periods.extend(sorted(month_periods, reverse=True))
        
        # Filtrar por período si se especifica
        if period_filter and period_filter in grouped_history:
            filtered_history = {period_filter: grouped_history[period_filter]}
            current_filter = period_filter
        else:
            # Filtrar períodos vacíos
            filtered_history = {k: v for k, v in grouped_history.items() if v}
            current_filter = None
        
        # Contar total de productos
        total_products = sum(len(products) for products in filtered_history.values())
        
        return request.render('theme_xtream.history_template', {
            'grouped_history': filtered_history,
            'available_periods': [period for period in available_periods if period in grouped_history and grouped_history[period]],
            'current_filter': current_filter,
            'total_products': total_products,
        })

    @http.route('/shop/history/remove/<int:product_id>', type='http', auth='user', website=True)
    def remove_from_history(self, product_id):
        user_id = request.env.user.id
        track_entries = request.env['website.track'].sudo().search([
            ('user_id', '=', user_id),
            ('product_id.product_tmpl_id', '=', product_id),
        ])
        if track_entries:
            track_entries.unlink()
        return request.redirect('/shop/history')
    
    @http.route('/shop/track_product/<int:product_tmpl_id>', type='http', auth='user', website=True)
    def track_product(self, product_tmpl_id, **kw):
        user = request.env.user
        if user._is_public():
            return ''  # Solo usuarios logueados
    
        product = request.env['product.product'].search([('product_tmpl_id', '=', product_tmpl_id)], limit=1)
        if not product:
            return ''
    
        url = request.httprequest.url  # Obtiene el URL actual
    
        # Guarda el historial
        request.env['product.view.history'].sudo().create({
            'user_id': user.id,
            'product_id': product.id,
            'url': url,
        })
    
        return 'OK'