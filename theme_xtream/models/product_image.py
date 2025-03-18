from odoo import models, fields

class ProductImage(models.Model):
    _name = 'product.image'
    _description = 'Product Additional Image'

    product_tmpl_id = fields.Many2one(
        'product.template', string="Product Template", required=True
    )
    image = fields.Binary(string="Image", required=True)
    name = fields.Char(string="Image Name")