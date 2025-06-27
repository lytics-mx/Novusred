from odoo import models, fields

class ProductImage(models.Model):
    _name = 'product.image'
    _description = 'Product Image'
    _order = 'sequence, id'

    name = fields.Char('Name')
    sequence = fields.Integer('Sequence', default=10)
    image_1920 = fields.Image('Image', max_width=1920, max_height=1920)
    product_tmpl_id = fields.Many2one('product.template', 'Product Template', required=True, ondelete='cascade')
    
    def name_get(self):
        result = []
        for record in self:
            name = f"Image {record.sequence}" if record.sequence else "Image"
            result.append((record.id, name))
        return result