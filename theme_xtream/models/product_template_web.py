from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    image_gallery_ids = fields.One2many(
        'product.image.gallery', 'product_tmpl_id', string="Image Gallery"
    )


class ProductImageGallery(models.Model):
    _name = 'product.image.gallery'
    _description = 'Product Image Gallery'

    product_tmpl_id = fields.Many2one('product.template', string="Product Template")
    image_url = fields.Char(string="Image URL", required=True)