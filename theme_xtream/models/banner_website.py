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
    # brand_images = fields.Many2many(
    #     'ir.attachment',
    #     'banner_brand_images_rel',
    #     'banner_id',
    #     'attachment_id',
    #     string="Brand Images",
    #     domain=[('mimetype', 'ilike', 'image/')],  # Only allow image files
    #     help="Upload images related to brands."
    # )

    # selected_categories = fields.Many2many(
    #     'product.category',
    #     'banner_category_rel',
    #     'banner_id',
    #     'category_id',
    #     string="Categorías Seleccionadas",
    #     help="Selecciona las categorías que quieres mostrar en el menú (ej: Auxiliar, Lámparas, etc.)"
    # )

    # category_menu_images = fields.Many2many(
    #     'ir.attachment',
    #     'banner_category_menu_images_rel',
    #     'banner_id',
    #     'attachment_id',
    #     string="Imágenes del Menú de Categorías",
    #     domain=[('mimetype', 'ilike', 'image/')],
    #     help="Sube las imágenes para el menú de categorías. Si subes 5 imágenes, debes seleccionar 5 categorías."
    # )



    is_active_carousel = fields.Boolean(string="Activar en el sitio web", default=False)
    is_active_product_carousel = fields.Boolean(string="Activar en el sitio web", default=False)
    # is_active_brand_carousel = fields.Boolean(string="Mostrar en Carrusel de Marcas", default=False)
    


    # @api.constrains('category_menu_images', 'selected_categories')
    # def _check_categories_images_count(self):
    #     """Valida que el número de categorías coincida con el número de imágenes"""
    #     for record in self:
    #         if record.category_menu_images and record.selected_categories:
    #             if len(record.category_menu_images) != len(record.selected_categories):
    #                 raise ValidationError(
    #                     f"Debes seleccionar exactamente {len(record.category_menu_images)} categorías "
    #                     f"para las {len(record.category_menu_images)} imágenes subidas."
    #                 )


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

    # @api.onchange('is_active_brand_carousel')
    # def _onchange_is_active_brand_carousel(self):
    #     """Ensure only one record is active for the brand carousel"""
    #     if self.is_active_brand_carousel:
    #         self.sudo().search([('id', '!=', self.id)]).write({'is_active_brand_carousel': False})