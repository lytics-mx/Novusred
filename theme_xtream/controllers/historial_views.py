from odoo import http
from odoo.http import request

class ProductHistoryController(http.Controller):

    @http.route('/shop/history', type='http', auth='user', website=True)
    def view_history(self):
        """Obtiene el historial de productos vistos por el usuario actual."""
        user_id = request.env.user.id
        history = request.env['product.view.history'].sudo().search(
            [('user_id', '=', user_id)], order='viewed_at desc'
        )
        # Agrega un print para depurar
        print("Historial obtenido:", history)
        return request.render('theme_xtream.history_template', {
            'history': history,
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
            print(f"Entrada del historial eliminada: {history_entry}")
        else:
            print(f"No se encontró la entrada del historial con ID: {history_id}")
        return request.redirect('/shop/history')