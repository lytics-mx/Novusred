from odoo import fields, models

class BannerImageLine(models.Model):
    """
    Model for individual images
    """
    _name = 'banner.image.line'
    _description = "Banner Image Line"

    general_images = fields.Many2many(
        'ir.attachment',
        'banner_general_images_rel',  # Nombre de la tabla de relación
        'banner_id',  # Campo que relaciona con este modelo
        'attachment_id',  # Campo que relaciona con ir.attachment
        string="General Images",
        domain=[('mimetype', 'ilike', 'image/')],  # Solo permite imágenes
        help="Upload general cover images."
    )
    
    product_images = fields.Many2many(
        'ir.attachment',
        'banner_product_images_rel',  # Nombre de la tabla de relación
        'banner_id',  # Campo que relaciona con este modelo
        'attachment_id',  # Campo que relaciona con ir.attachment
        string="Product Images",
        domain=[('mimetype', 'ilike', 'image/')],  # Solo permite imágenes
        help="Upload product cover images."
    )