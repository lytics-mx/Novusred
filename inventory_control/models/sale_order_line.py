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
            
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            display_type = vals.get('display_type')
            # Solo validar si NO es nota ni sección
            if display_type not in ('line_section', 'line_note') and not vals.get('product_id'):
                raise ValidationError(_("Debe seleccionar un producto para cada línea de pedido."))
        return super().create(vals_list)
    
    def write(self, vals):
        for line in self:
            display_type = vals.get('display_type', line.display_type)
            product_id = vals.get('product_id', line.product_id.id)
            # Solo validar si NO es nota ni sección
            if display_type not in ('line_section', 'line_note') and not product_id:
                raise ValidationError(_("Debe seleccionar un producto para cada línea de pedido."))
        return super().write(vals)
