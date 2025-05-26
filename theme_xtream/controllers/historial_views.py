from odoo import http
from odoo.http import request
from collections import defaultdict
from datetime import datetime, timedelta
from babel.dates import format_date

class ProductHistoryController(http.Controller):

    @http.route('/shop/history', type='http', auth='user', website=True)
    def view_history(self):
        """Obtiene el historial de productos vistos por el usuario actual."""
        user_id = request.env.user.id
        history = request.env['product.view.history'].sudo().search(
            [('user_id', '=', user_id)], order='viewed_at desc'
        )

        # Agrupar productos por fecha
        grouped_history = defaultdict(list)
        today = datetime.now().date()
        
        for entry in history:
            # Obtener la fecha del entry
            entry_date = entry.viewed_at.date()
            
            # Si es hoy, mostrar en grupo "Hoy"
            if entry_date == today:
                display_name = "Hoy"
            else:
                # Para otros días, mostrar por mes
                month_name = format_date(entry.viewed_at, format='MMMM', locale=request.env.user.lang)
                year = entry.viewed_at.strftime('%Y')
                display_name = f"{month_name} {year}"
            
            grouped_history[display_name].append(entry)

        # Ordenar los meses (primero "Hoy", luego los demás meses en orden cronológico inverso)
        # Usamos una clave personalizada para ordenar: "0" para "Hoy", y el nombre del mes para el resto
        sorted_months = sorted(grouped_history.keys(), 
                               key=lambda x: ("0" if x == "Hoy" else x.split()[0]),
                               reverse=False)
        
        sorted_history = {month: grouped_history[month] for month in sorted_months}
        
        # Pasar los datos agrupados al template
        return request.render('theme_xtream.history_template', {
            'grouped_history': sorted_history,
        })

    @http.route('/shop/history/remove/<int:product_id>', type='json', auth='user', website=True)
    def remove_from_history(self, product_id):
        """Elimina un producto del historial del usuario actual."""
        user_id = request.env.user.id
        
        # Buscar todos los registros de este producto en el historial del usuario
        history_entries = request.env['product.view.history'].sudo().search([
            ('user_id', '=', user_id),
            ('product_id', '=', product_id)
        ])

        # Eliminar los registros si existen
        if history_entries:
            history_entries.unlink()
            return {'success': True}
        
        return {'success': False}