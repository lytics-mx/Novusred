from odoo import models, fields, api

class ProductTag(models.Model):
    _inherit = 'product.tag'

    is_fixed_discount = fields.Boolean(
        string="¿Descuento Fijo?",
        help="Si está activado, el descuento será una cantidad fija. Si no, será un porcentaje."
    )

    discount_value = fields.Float(
        string="Valor del Descuento",
        help="Valor del descuento. Puede ser un porcentaje o una cantidad fija dependiendo de la configuración."
    )

    def write(self, vals):
        """Aplica el descuento a los productos relacionados al guardar."""
        res = super(ProductTag, self).write(vals)
        if 'is_fixed_discount' in vals or 'discount_value' in vals:
            for tag in self:
                products = self.env['product.template'].search([('tag_ids', 'in', tag.id)])
                products._compute_discount_from_tags()
                products._compute_discounted_price()
        return res