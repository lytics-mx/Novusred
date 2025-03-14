from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def create_quant_for_consumables(self):
        # Verifica si el tipo de producto es consumible y si es necesario agregar stock quant
        for product in self:
            if product.type in ['consu', 'service']:  # Acepta consumibles y servicios
                # Si es necesario, crea un quant en stock
                quant_vals = {
                    'product_id': product.id,
                    'quantity': product.qty_available,  # Establece la cantidad que desees
                    'location_id': 1,  # Asocia a una ubicación
                    'in_date': fields.Datetime.now(),
                }
                self.env['stock.quant'].create(quant_vals)

