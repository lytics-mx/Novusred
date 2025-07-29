from odoo import http
from odoo.http import request

class CheckoutController(http.Controller):
    @http.route('/tienda/checkout', type='http', auth='public', website=True)
    def checkout_page(self):
        # Obtener la información del usuario actual
        partner = request.env.user.partner_id

        # Obtener los productos del carrito
        cart_items = request.env['sale.order'].sudo().search([
            ('partner_id', '=', partner.id),
            ('state', '=', 'draft')
        ])

        # Calcular el total, impuestos y otros detalles
        total = sum(item.price_total for item in cart_items.order_line)
        taxes = sum(item.price_tax for item in cart_items.order_line)
        subtotal = total - taxes

        # Contexto para el template
        context = {
            'partner': partner,
            'cart_items': cart_items,
            'subtotal': subtotal,
            'taxes': taxes,
            'total': total,
        }
        return request.render('theme_xtream.checkout_template', context)