from odoo import models, api, fields

class UpdateSaleOrderSequence(models.Model):
    _inherit = 'sale.order'
    # Cambiar el nombre del campo "Vendedor" a "Ejecutivo de cuenta"
    user_id = fields.Many2one(
        'res.users',
        string="Ejecutivo de cuenta",
        tracking=True,
        default=lambda self: self.env.user
    )
    @api.model
    def update_sale_order_sequence(self):
        # Buscar la secuencia de las órdenes de venta
        sequence = self.env['ir.sequence'].search([('code', '=', 'sale.order')], limit=1)
        if sequence:
            # Actualizar el prefijo y el número inicial
            sequence.write({
                'prefix': 'S',
                'number_next': 23500
            })

    def action_update_sequence(self):
        # Llamar al método para actualizar la secuencia
        self.update_sale_order_sequence()