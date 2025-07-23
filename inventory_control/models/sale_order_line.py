from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_model = fields.Char(
        string="Modelo",
        related='product_id.product_tmpl_id.product_model',
        store=True,
        readonly=True
    )

    product_id = fields.Many2one(
        'product.product',
        string='Producto',
        domain=[('sale_ok', '=', True)],
        required=True
    )

    
    def name_get(self):
        result = []
        for product in self.product_id:
            name = f"{product.product_model or ''} - {product.name or ''}"
            result.append((product.id, name))
        return result
