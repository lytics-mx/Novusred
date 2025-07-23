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
                # Supongamos que 'product_model' es un campo en product.product
                product_model = getattr(line.product_id, 'product_model', False)
                product_name = line.product_id.name or ''

                # Asignar: primero product_model + espacio + product_name (sin default_code)
                if product_model:
                    line.name = f"{product_model} {product_name}"
                else:
                    line.name = product_name
            else:
                line.name = ''