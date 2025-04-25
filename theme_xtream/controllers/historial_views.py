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

    @http.route('/shop/history/remove/<int:product_id>', type='http', auth='user', methods=['POST'], website=True)
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