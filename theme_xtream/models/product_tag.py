from odoo import models, fields, api
from datetime import date

class ProductTag(models.Model):
    _inherit = 'product.tag'

    discount_percentage = fields.Float(
        string="Descuento",
        help="Porcentaje o cantidad de descuento aplicado a los productos con esta etiqueta."
    )

    is_percentage = fields.Boolean(
        string="¿Es porcentaje?",
        default=True,
        help="Si está activado, el descuento se interpreta como un porcentaje. Si no, como una cantidad fija."
    )

    expiration_date = fields.Date(
        string="Fecha de expiración",
        help="Fecha en la que esta etiqueta será eliminada automáticamente de los productos."
    )

    def write(self, vals):
        """Aplica el descuento a los productos relacionados al guardar."""
        res = super(ProductTag, self).write(vals)
        if 'discount_percentage' in vals or 'is_percentage' in vals:
            for tag in self:
                products = self.env['product.template'].search([('product_tag_ids', 'in', tag.id)])
                products._compute_discount_percentage_from_tags()
                products._compute_discounted_price()
        return res

    @api.model
    def _remove_expired_tags(self):
        """Elimina etiquetas expiradas de los productos."""
        today = date.today()
        expired_tags = self.search([('expiration_date', '<=', today)])
        for tag in expired_tags:
            products = self.env['product.template'].search([('product_tag_ids', 'in', tag.id)])
            for product in products:
                product.write({'product_tag_ids': [(3, tag.id)]})  # Elimina la etiqueta del producto