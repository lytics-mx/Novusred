# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import fields, models


class XtreamTestimonials(models.Model):
    """
    Model for testimonials
    """
    _name = 'xtream.testimonials'
    _description = "Xtream Testimonials"

    partner_id = fields.Many2one("res.partner", required=True,
                                 help="Select the customer providing the"
                                      "testimony",
                                 domain="[('is_company', '=', False)]")
    testimony = fields.Text(string="Testimony", required=True,
                            help="Enter the testimonial provided by the"
                                 "customer")


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Redefinir el campo image_1920 como Many2many
    image_1920 = fields.Many2many(
        'ir.attachment',
        'product_template_image_1920_rel',  # Relación con imágenes
        'product_id',  # Relación al producto
        'attachment_id',  # Relación al archivo
        string='Product Images',
        domain=[('mimetype', 'ilike', 'image/')],  # Solo imágenes
        help="Upload multiple images for this product to display on the website."
      )

    def get_website_images(self):
        """
        Método para obtener todas las imágenes del producto para mostrar en el sitio web.
        """
        return self.image_1920.filtered(lambda img: img.mimetype.startswith('image/'))

    def get_main_image(self):
        """
        Método para obtener la imagen principal del producto.
        """
        return self.image_1920[:1] if self.image_1920 else False

    def get_additional_website_images(self):
        """
        Método para obtener imágenes adicionales del producto.
        """
        return self.image_1920[1:] if len(self.image_1920) > 1 else []