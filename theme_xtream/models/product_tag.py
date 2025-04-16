from odoo import models, fields, api

class ProductTag(models.Model):
    _inherit = 'product.tag'

    discount_percentage = fields.Float(
        string="Descuento (%)",
        help="Porcentaje de descuento aplicado a los productos con esta etiqueta."
    )
    discount_value = fields.Float(
        string="Descuento",
        help="Valor del descuento. Si es < 1, se interpreta como porcentaje. Si es >= 1, se interpreta como descuento fijo (en pesos)."
    )

    @api.constrains('discount_value')
    def _check_discount_value(self):
        """Valida que el descuento sea un valor positivo."""
        for tag in self:
            if tag.discount_value < 0:
                raise ValueError("El valor del descuento no puede ser negativo.")
            
    def write(self, vals):
        """Aplica el descuento a los productos relacionados al guardar."""
        res = super(ProductTag, self).write(vals)
        if 'discount_percentage' in vals:
            for tag in self:
                products = self.env['product.template'].search([('tag_ids', 'in', tag.id)])
                products._compute_discount_percentage_from_tags()
                products._compute_discounted_price()
        return res
    
   