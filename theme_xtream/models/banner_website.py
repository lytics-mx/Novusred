from odoo import fields, models

class BannerImageLine(models.Model):
    """
    Model for individual images
    """
    _name = 'banner.image.line'
    _description = "Banner Image Line"

    image_set_id = fields.Many2one(
        'banner.images', string="Image Set",
        required=True, ondelete='cascade'
    )
    image = fields.Binary(string="Image", required=True, help="Upload the image")
    description = fields.Char(string="Description", help="Description of the image")