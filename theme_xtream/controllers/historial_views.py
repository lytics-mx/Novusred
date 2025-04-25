from odoo import http
from odoo.http import request
from collections import defaultdict

class ProductHistoryController(http.Controller):

    @http.route('/shop/history', type='http', auth='user', website=True)
    def view_history(self):
        """Obtiene el historial de productos vistos por el usuario actual, incluyendo los ocultos si se vuelven a visitar."""
        user_partner_id = request.env.user.partner_id.id
        history = request.env['website.track'].sudo().search([
            ('visitor_id.partner_id', '=', user_partner_id),
            '|',  # Mostrar productos no ocultos o que han sido visitados nuevamente
            ('hidden', '=', False),
            ('hidden', '=', True)
        ], order='create_date desc')
    
        # Pasar los datos al template
        return request.render('theme_xtream.history_template', {
            'viewed_products': history.mapped('product_id.product_tmpl_id'),
        })
    @http.route('/shop/history/remove/<int:product_id>', type='http', auth='user', website=True)
    def remove_from_history(self, product_id):
        """Oculta un producto del historial del usuario actual en lugar de eliminarlo."""
        user_partner_id = request.env.user.partner_id.id
        # Buscar el registro en el historial
        track_entry = request.env['website.track'].sudo().search([
            ('visitor_id.partner_id', '=', user_partner_id),
            ('product_id.product_tmpl_id', '=', product_id)
        ], limit=1)
    
        # Marcar como oculto si existe
        if track_entry:
            track_entry.sudo().write({'hidden': True})
    
        # Redirigir de vuelta al historial
        return request.redirect('/shop/history')