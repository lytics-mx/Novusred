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

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('product_id'):
                raise ValidationError(_("Debe seleccionar un producto para cada línea de pedido."))
        return super().create(vals_list)

    def write(self, vals):
        if 'product_id' in vals and not vals.get('product_id'):
            raise ValidationError(_("Debe seleccionar un producto para cada línea de pedido."))
        return super().write(vals)