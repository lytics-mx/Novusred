from odoo import fields, models

class BannerImages(models.Model):
    """
    Model for managing banner images
    """
    _name = 'banner.images'
    _description = "Banner Images"

    name = fields.Char(string="Name", required=True, help="Name of the image set")
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