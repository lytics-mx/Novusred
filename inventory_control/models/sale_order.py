from odoo import models, api, fields

class UpdateSaleOrderSequence(models.Model):
    _inherit = 'sale.order'

    # Sobrescribir el campo 'note' para que siempre tenga el valor "Ejecutivo de cuenta"
    note = fields.Text(
        string="Ejecutivo de cuenta",  # Cambiar la etiqueta del campo a "Ejecutivo de cuenta"
        default="Ejecutivo de cuenta",  # Establecer un valor predeterminado
        required=False
    )

    @api.model
    def create(self, vals):
        # Forzar el valor de 'note' al crear un nuevo registro
        vals['note'] = "Ejecutivo de cuenta"
        return super().create(vals)

    def write(self, vals):
        # Forzar el valor de 'note' al actualizar un registro
        vals['note'] = "Ejecutivo de cuenta"
        return super().write(vals)

    @api.model
    def update_existing_notes(self):
        # Actualizar todos los registros existentes para que el campo 'note' sea "Ejecutivo de cuenta"
        orders = self.search([])
        orders.write({'note': "Ejecutivo de cuenta"})


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