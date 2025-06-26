from odoo import models, fields, api

class ProductImage(models.Model):
    _name = 'product.image'
    _description = 'Product Additional Images'
    _order = 'sequence, id'

    name = fields.Char(string='Name', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    image_1920 = fields.Image(string='Image', max_width=1920, max_height=1920)
    image_1024 = fields.Image(string='Image 1024', related='image_1920', max_width=1024, max_height=1024, store=True)
    image_512 = fields.Image(string='Image 512', related='image_1920', max_width=512, max_height=512, store=True)
    image_256 = fields.Image(string='Image 256', related='image_1920', max_width=256, max_height=256, store=True)
    image_128 = fields.Image(string='Image 128', related='image_1920', max_width=128, max_height=128, store=True)
    
    # This is the missing field that's causing the KeyError
    product_tmpl_id = fields.Many2one(
        'product.template',
        string='Product Template',
        required=True,
        ondelete='cascade'
    )