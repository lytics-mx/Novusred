from odoo import models, api, fields

class UpdateSaleOrderSequence(models.Model):
    _inherit = 'sale.order'
    

    @api.model
    def create(self, vals):
        # Solo establece el valor de 'note' si no existe en los valores proporcionados
        if 'note' not in vals or not vals['note']:
            vals['note'] = "Términos y Condiciones en: https://novusred.mx/content/2-Terminos-y-Condiciones"
        return super().create(vals)

    def write(self, vals):
        # Solo establece el valor de 'note' si no existe en los valores proporcionados
        if 'note' not in vals or not vals['note']:
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