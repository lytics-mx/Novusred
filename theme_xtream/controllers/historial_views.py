from odoo import http
from odoo.http import request
from collections import defaultdict

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
        for entry in history:
            month = entry.viewed_at.strftime('%B %Y')
            grouped_history[month].append(entry)

        # Pasar los datos agrupados al template
        return request.render('theme_xtream.history_template', {
            'grouped_history': dict(grouped_history),
        })

    @http.route('/shop/history/remove/<int:history_id>', type='http', auth='user', website=True)
    def remove_from_history(self, history_id):
        """Elimina un producto del historial del usuario actual."""
        user_id = request.env.user.id
        history_entry = request.env['product.view.history'].sudo().search(
            [('id', '=', history_id), ('user_id', '=', user_id)], limit=1
        )
        if history_entry:
            history_entry.unlink()
        return request.redirect('/shop/history')