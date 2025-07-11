from odoo import http
from odoo.http import request

class WebsiteCheckout(http.Controller):
    @http.route(['/delivered_products'], type='http', auth='user', website=True)
    def delivered_products(self):
        user = request.env.user
        delivered_pickings = request.env['stock.picking'].sudo().search([
            ('state', '=', 'done'),
            ('partner_id', '=', user.partner_id.id)
        ])
        return request.render('theme_xtream.delivered_template', {
            'delivered_pickings': delivered_pickings,
        })