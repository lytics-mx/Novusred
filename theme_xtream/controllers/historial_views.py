# from odoo import http
# from odoo.http import request

# class ProductHistoryController(http.Controller):

#     @http.route('/shop/history', type='http', auth='user', website=True)
#     def view_history(self):
#         """Obtiene el historial de productos vistos por el usuario actual."""
#         user_id = request.env.user.id
#         history = request.env['product.view.history'].sudo().search([('user_id', '=', user_id)], order='viewed_at desc')
#         return request.render('theme_xtream.history_template', {
#             'history': history,
#         })