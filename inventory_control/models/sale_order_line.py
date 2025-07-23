from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_model = fields.Char(
        string="Modelo",
        related='product_id.product_tmpl_id.product_model',
        store=True,
        readonly=True
    )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for line in self:
            if line.product_id:
                # Solo asignar el nombre sin código
                line.name = line.product_id.name
            else:
                line.name = ''
