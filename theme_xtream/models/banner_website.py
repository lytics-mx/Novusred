from odoo import fields, models, api
from odoo import fields, models, api
from odoo.exceptions import ValidationError

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
        string="Imágenes de la sección",
        domain=[('mimetype', 'ilike', 'image/')],
        help="Upload general cover images."
    )
    product_images = fields.Many2many(
        'ir.attachment',
        'banner_product_images_rel',
        'banner_id',
        'attachment_id',
        string="Imágenes de la sección",
        domain=[('mimetype', 'ilike', 'image/')],
        help="Upload product cover images."
    )

    is_active_carousel = fields.Boolean(string="Activar en el sitio web", default=False)
    is_active_product_carousel = fields.Boolean(string="Activar en el sitio web", default=False)


    @api.onchange('is_active_product_carousel')
    def _onchange_is_active_product_carousel(self):
        """Asegura que solo un registro esté activo en el carrusel de productos"""
        if self.is_active_product_carousel:
            self.sudo().search([('id', '!=', self.id)]).write({'is_active_product_carousel': False})
 
    @api.onchange('is_active_carousel')
    def _onchange_is_active_carousel(self):
        """Asegura que solo un registro esté activo en el carrusel"""
        if self.is_active_carousel:
            self.sudo().search([('id', '!=', self.id)]).write({'is_active_carousel': False}) 

