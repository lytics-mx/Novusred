from odoo import fields, models

class BannerImageLine(models.Model):
    """
    Model for individual images
    """
    _name = 'banner.image.line'
    _description = "Banner Image Line"

    name = fields.Char(string="Name", help="Name of the image set")
    general_images = fields.Many2many(
        'ir.attachment',
        'banner_general_images_rel',
        'banner_id',
        'attachment_id',
        string="General Images",
        domain=[('mimetype', 'ilike', 'image/')],
        help="Upload general cover images."
    )
    product_images = fields.Many2many(
        'ir.attachment',
        'banner_product_images_rel',
        'banner_id',
        'attachment_id',
        string="Product Images",
        domain=[('mimetype', 'ilike', 'image/')],
        help="Upload product cover images."
    )