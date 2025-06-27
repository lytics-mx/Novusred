from odoo import http
from odoo.http import request
from datetime import datetime, timedelta
import pytz

class ProductHistoryController(http.Controller):

    @http.route(['/shop/history', '/shop/history/<string:period_filter>'], type='http', auth='user', website=True)
    def view_history(self, period_filter=None):
        """Obtiene el historial de productos vistos por el usuario actual agrupado por períodos."""
        user_partner_id = request.env.user.partner_id.id
        
        # Obtener todas las visitas del usuario
        tracks = request.env['website.track'].sudo().search([
            ('visitor_id.partner_id', '=', user_partner_id),
            ('product_id', '!=', False)
        ], order='visit_datetime desc')
        
        # Configurar zona horaria
        user_tz = pytz.timezone(request.env.user.tz or 'UTC')
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
        
        for track in tracks:
            visit_date = track.visit_datetime.astimezone(user_tz).date()
            product = track.product_id.product_tmpl_id
            
            if visit_date == today:
                grouped_history['Hoy'].append(product)
            elif visit_date == yesterday:
                grouped_history['Ayer'].append(product)
            elif visit_date >= week_start and visit_date < yesterday:
                grouped_history['Esta semana'].append(product)
            elif visit_date >= month_start and visit_date < week_start:
                grouped_history['Este mes'].append(product)
            else:
                grouped_history['Anteriores'].append(product)
        
        # Filtrar por período si se especifica
        if period_filter and period_filter in grouped_history:
            filtered_history = {period_filter: grouped_history[period_filter]}
        else:
            filtered_history = {k: v for k, v in grouped_history.items() if v}
        
        return request.render('theme_xtream.history_template', {
            'grouped_history': filtered_history,
        })

    @http.route('/shop/history/add/<int:product_id>', type='http', auth='user', website=True)
    def add_to_history(self, product_id):
        """Agrega un producto al historial del usuario actual."""
        visitor_id = request.env['website.visitor']._get_visitor_from_request().id
        if visitor_id and product_id:
            request.env['website.track'].sudo().create({
                'visitor_id': visitor_id,
                'product_id': product_id,
                'visit_datetime': datetime.now(),
            })
        return request.redirect('/shop/history')