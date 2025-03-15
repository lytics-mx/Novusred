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


class ProductProduct(models.Model):
     _inherit = 'product.product'

     image_ids = fields.Many2many(
          'ir.attachment',
          'product_product_image_rel',  # Relación con las imágenes
          'product_id',  # Relación al producto
          'attachment_id',  # Relación con el archivo
          string='Imágenes adicionales',
          domain=[('mimetype', 'ilike', 'image/')],  # Limitado solo a imágenes
          help="Sube múltiples imágenes adicionales para este producto."
     )

     def get_website_images(self):
          """
          Método para obtener las imágenes adicionales del producto
          que se mostrarán en el sitio web.
          """
          return self.image_ids.filtered(lambda img: img.mimetype.startswith('image/'))

     def get_main_image(self):
          """
          Método para obtener la primera imagen que se mostrará en Odoo.
          """
          return self.image_1920 if self.image_1920 else False

     def get_additional_website_images(self):
          """
          Método para obtener todas las imágenes adicionales excepto la principal.
          """
          return self.get_website_images().filtered(lambda img: img != self.image_1920)
