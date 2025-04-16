from odoo import models, fields

class ProductTag(models.Model):
    _name = 'product.tag'
    _description = 'Product Tag'

    discount_percentage = fields.Float(string="Descuento (%)", help="Porcentaje de descuento asociado a esta etiqueta.")
    product_ids = fields.Many2many(
        'product.template',
        'product_template_tag_rel',  # Nombre de la tabla de relación
        'tag_id',  # Campo de relación a la etiqueta
        'product_id',  # Campo de relación al producto
        string="Productos Relacionados",
        help="Productos asociados con esta etiqueta."
    )

    def write(self, vals):
        """Actualiza automáticamente el campo tag_ids en los productos relacionados."""
        res = super(ProductTag, self).write(vals)
        if 'product_ids' in vals:
            for tag in self:
                # Actualiza el campo tag_ids en los productos relacionados
                tag.product_ids.write({'tag_ids': [(4, tag.id)]})
        return res

    def create(self, vals):
        """Asegura que los productos relacionados se actualicen al crear una etiqueta."""
        tag = super(ProductTag, self).create(vals)
        if 'product_ids' in vals:
            tag.product_ids.write({'tag_ids': [(4, tag.id)]})
        return tag