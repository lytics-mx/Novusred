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

    @api.model
    def create(self, vals):
        if 'product_id' in vals:
            product = self.env['product.product'].browse(vals['product_id'])
            product_model = getattr(product, 'product_model', False)
            product_name = product.name or ''
            vals['name'] = f"{product_model or ''} {product_name}"
        return super(SaleOrderLine, self).create(vals)

    def write(self, vals):
        if 'product_id' in vals:
            product = self.env['product.product'].browse(vals['product_id'])
            product_model = getattr(product, 'product_model', False)
            product_name = product.name or ''
            vals['name'] = f"{product_model or ''} {product_name}"
        return super(SaleOrderLine, self).write(vals)