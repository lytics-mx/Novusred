from odoo import http
from odoo.http import request
from datetime import datetime, timedelta
import pytz

class ProductHistoryController(http.Controller):

    @http.route('/shop/product/<int:product_id>', type='http', auth='public', website=True)
    def product_page(self, product_id, **kwargs):
        product = request.env['product.product'].sudo().browse(product_id)
        if product.exists():
            # Registrar el producto en el historial
            if request.env.user.id:
                request.env['product.view.history'].sudo().add_product_to_history(product_id)

            return request.render('theme_xtream.product_template', {'product': product})
        return request.not_found()


    def _get_month_name_spanish(self, date):
        """Convierte una fecha a nombre de mes en español."""
        months_spanish = {
            1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
            5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
            9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
        }
        return months_spanish[date.month]

    @http.route(['/shop/history', '/shop/history/<string:period_filter>'], type='http', auth='user', website=True)
    def view_history(self, period_filter=None):
        """Obtiene el historial de productos vistos agrupados por períodos."""
        user_id = request.env.user.id
        user_tz = pytz.timezone('America/Mexico_City')  # Ajusta la zona horaria según sea necesario
        today = datetime.now(user_tz).date()
        yesterday = today - timedelta(days=1)
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)

        # Obtener todos los registros de historial del usuario actual
        history_records = request.env['product.view.history'].sudo().search([
            ('user_id', '=', user_id)
        ], order='viewed_at desc')

        # Agrupar productos por períodos
        grouped_history = {
            'Hoy': [],
            'Ayer': [],
            'Esta semana': [],
            'Este mes': [],
        }
        month_periods = set()

        for record in history_records:
            viewed_date = record.viewed_at.astimezone(user_tz).date()
            product = record.product_id

            if viewed_date == today:
                grouped_history['Hoy'].append({'product': product, 'viewed_at': record.viewed_at})
            elif viewed_date == yesterday:
                grouped_history['Ayer'].append({'product': product, 'viewed_at': record.viewed_at})
            elif viewed_date >= week_start and viewed_date < yesterday:
                grouped_history['Esta semana'].append({'product': product, 'viewed_at': record.viewed_at})
            elif viewed_date >= month_start and viewed_date < week_start:
                grouped_history['Este mes'].append({'product': product, 'viewed_at': record.viewed_at})
            else:
                month_name = self._get_month_name_spanish(viewed_date)
                month_periods.add(month_name)
                if month_name not in grouped_history:
                    grouped_history[month_name] = []
                grouped_history[month_name].append({'product': product, 'viewed_at': record.viewed_at})

        # Filtrar períodos vacíos
        filtered_grouped_history = {k: v for k, v in grouped_history.items() if v}

        # Lista de períodos disponibles
        available_periods = ['Hoy', 'Ayer', 'Esta semana', 'Este mes'] + sorted(month_periods, reverse=True)

        # Filtrar por período si se especifica
        if period_filter and period_filter in grouped_history:
            filtered_history = {period_filter: grouped_history[period_filter]}
            current_filter = period_filter
        else:
            filtered_history = filtered_grouped_history
            current_filter = None

        return request.render('theme_xtream.history_template', {
            'grouped_history': filtered_history,
            'available_periods': available_periods,
            'current_filter': current_filter,
        })

    @http.route('/shop/history/remove/<int:product_id>', type='http', auth='user', website=True)
    def remove_from_history(self, product_id):
        """Elimina un producto del historial del usuario actual."""
        user_id = request.env.user.id

        # Buscar todos los registros de este producto para este usuario
        history_records = request.env['product.view.history'].sudo().search([
            ('user_id', '=', user_id),
            ('product_id', '=', product_id)
        ])

        # Eliminar todos los registros
        if history_records:
            history_records.unlink()

        # Redirigir de vuelta al historial
        return request.redirect('/shop/history')