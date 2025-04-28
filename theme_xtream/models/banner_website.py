from odoo import fields, models


class BannerImages(models.Model):
    """
    Model for managing images
    """
    _name = 'banner.images'
    _description = "Xtream Images"

    name = fields.Char(string="Name", required=True, help="Name of the image set")
    image_quantity = fields.Selection([
        ('2', '2 Images'),
        ('4', '4 Images'),
        ('8', '8 Images'),
        ('12', '12 Images'),
        ('14', '14 Images')
    ], string="Number of Cover Images", default='2', required=True)
    
    product_image_quantity = fields.Selection([
        ('2', '2 Images'),
        ('4', '4 Images'),
        ('8', '8 Images'),
        ('12', '12 Images'),
        ('14', '14 Images')
    ], string="Number of Product Images", default='2', required=True)
    
    cover_images = fields.One2many(
        'banner.image.line', 'image_set_id',
        string="Cover Images",
        help="Upload multiple cover images"
    )
    product_cover_images = fields.One2many(
        'banner.image.line', 'image_set_id',
        string="Product Cover Images",
        help="Upload multiple product cover images"
    )


