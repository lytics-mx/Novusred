from odoo import fields, models, api

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

    is_active_carousel = fields.Boolean(string="Mostrar en Portada", default=False)

    @api.onchange('is_active_carousel')
    def _onchange_is_active_carousel(self):
        """Asegura que solo un registro esté activo en el carrusel"""
        if self.is_active_carousel:
            self.sudo().search([('id', '!=', self.id)]).write({'is_active_carousel': False}) 