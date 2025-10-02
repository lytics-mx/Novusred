from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_model = fields.Char(
        string="Modelo",
        related='product_id.product_tmpl_id.product_model',
        store=True,
        readonly=True
    )
    

    
    def name_get(self):
        result = []
        for line in self:
            name = f"{line.product_model or ''} - {line.product_id.name or ''}"
            result.append((line.id, name))
        return result
