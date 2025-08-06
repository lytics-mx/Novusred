from odoo import models, api, fields

class UpdateSaleOrderSequence(models.Model):
    _inherit = 'sale.order'
    
    note = fields.Text(
        default="Términos y Condiciones en: https://novusred.mx/content/2-Terminos-y-Condiciones",
        required=False
    )

    @api.model
    def create(self, vals):
        # Fuerza el valor del campo note al crear, sobrescribiendo el predeterminado de Odoo
        vals['note'] = "Términos y Condiciones en: https://novusred.mx/content/2-Terminos-y-Condiciones"
        return super().create(vals)

    def write(self, vals):
        # Fuerza el valor del campo note al actualizar, sobrescribiendo el predeterminado de Odoo
        vals['note'] = "Términos y Condiciones en: https://novusred.mx/content/2-Terminos-y-Condiciones"
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