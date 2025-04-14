from odoo import models, fields, api

class ProductTag(models.Model):
    _inherit = 'product.tag'

    discount_percentage = fields.Float(
        string="Descuento (%)",
        help="Porcentaje de descuento aplicado a los productos con esta etiqueta."
    )

    @api.onchange('discount_percentage')
    def _onchange_discount_percentage(self):
        """Aplica el descuento automáticamente a las plantillas de producto relacionadas."""
        for tag in self:
            if tag.discount_percentage >= 0:
                products = self.env['product.template'].search([('tag_ids', 'in', tag.id)])
                for product in products:
                    product.discount_percentage = tag.discount_percentage

    def write(self, vals):
        """Aplica el descuento a los productos relacionados al guardar."""
        res = super(ProductTag, self).write(vals)
        if 'discount_percentage' in vals:
            for tag in self:
                products = self.env['product.template'].search([('tag_ids', 'in', tag.id)])
                for product in products:
                    product.discount_percentage = tag.discount_percentage
        return res