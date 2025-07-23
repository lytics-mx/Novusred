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
                # Asignar solo el código interno (default_code) o el nombre corto si no hay código
                line.name = line.product_id.default_code or line.product_id.name
            else:
                line.name = ''