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
        for product in self.product_id:
            name = f"{product.product_model or ''} - {product.name or ''}"
            result.append((product.id, name))
        return result
            
