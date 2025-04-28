from odoo import fields, models


class BannerImages(models.Model):
    """
    Model for managing banner images
    """
    _name = 'banner.images'
    _description = "Banner Images"

    name = fields.Char(string="Name", required=True, help="Name of the image set")
    
    general_images = fields.Many2many(
        'ir.attachment',
        'banner_general_images_rel',  # Nombre de la tabla de relación
        'banner_id',  # Campo que relaciona con este modelo
        'attachment_id',  # Campo que relaciona con ir.attachment
        string="General Images",
        domain=[('mimetype', 'ilike', 'image/')],  # Solo permite imágenes
        help="Sube imágenes generales."
    )
    
    product_images = fields.Many2many(
        'ir.attachment',
        'banner_product_images_rel',  # Nombre de la tabla de relación
        'banner_id',  # Campo que relaciona con este modelo
        'attachment_id',  # Campo que relaciona con ir.attachment
        string="Product Images",
        domain=[('mimetype', 'ilike', 'image/')],  # Solo permite imágenes
        help="Sube imágenes de productos."
    )