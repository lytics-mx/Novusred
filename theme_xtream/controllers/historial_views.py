from odoo import http
from odoo.http import request
from collections import defaultdict
from datetime import datetime
from babel.dates import format_date

class ProductHistoryController(http.Controller):

    @http.route('/shop/history', type='http', auth='user', website=True)
    def view_history(self):
        """Obtiene el historial de productos vistos por el usuario actual."""
        user_id = request.env.user.id
        history = request.env['product.view.history'].sudo().search(
            [('user_id', '=', user_id)], order='viewed_at desc'
        )

        # Agrupar productos por mes
        grouped_history = defaultdict(list)
        current_month = datetime.now().strftime('%Y-%m')
        
        for entry in history:
            # Formato año-mes para ordenar correctamente
            month_key = entry.viewed_at.strftime('%Y-%m')
            
            # Nombre localizado del mes para mostrar
            month_name = format_date(entry.viewed_at, format='MMMM', locale=request.env.user.lang)
            year = entry.viewed_at.strftime('%Y')
            display_name = f"{month_name} {year}"
            
            # Categoría especial para "Hoy"
            if month_key == current_month:
                if entry.viewed_at.date() == datetime.now().date():
                    display_name = "Hoy"
            
            grouped_history[display_name].append(entry)

        # Ordenar los meses (primero "Hoy", luego los demás meses en orden cronológico inverso)
        sorted_months = sorted(grouped_history.keys(), 
                               key=lambda x: "0" if x == "Hoy" else x,
                               reverse=True)
        
        sorted_history = {month: grouped_history[month] for month in sorted_months}
        
        # Pasar los datos agrupados al template
        return request.render('theme_xtream.history_template', {
            'grouped_history': sorted_history,
        })
    @http.route('/shop/history/remove/<int:product_id>', type='http', auth='user', website=True)
    def remove_from_history(self, product_id):
        """Elimina un producto del historial del usuario actual."""
        user_partner_id = request.env.user.partner_id.id
        # Buscar el registro en el historial
        track_entry = request.env['website.track'].sudo().search([
            ('visitor_id.partner_id', '=', user_partner_id),
            ('product_id.product_tmpl_id', '=', product_id)
        ], limit=1)

        # Eliminar el registro si existe
        if track_entry:
            track_entry.unlink()

        # Redirigir de vuelta al historial
        return request.redirect('/shop/history')
    

