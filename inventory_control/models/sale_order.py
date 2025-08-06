from odoo import models, api, fields

class UpdateSaleOrderSequence(models.Model):
    _inherit = 'sale.order'

    # Cambiar el nombre del campo "Vendedor" a "Ejecutivo de cuenta"
    user_id = fields.Many2one(
        'res.users',
        string="Ejecutivo de cuenta",  # Cambiar la etiqueta del campo a "Ejecutivo de cuenta"
        tracking=True,
        default=lambda self: self.env.user
    )

    @api.model
    def create(self, vals):
        # Forzar el valor de 'user_id' al crear un nuevo registro si no está definido
        if 'user_id' not in vals:
            vals['user_id'] = self.env.user.id
        return super().create(vals)

    def write(self, vals):
        # Forzar el valor de 'user_id' al actualizar un registro si no está definido
        if 'user_id' not in vals:
            vals['user_id'] = self.env.user.id
        return super().write(vals)



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