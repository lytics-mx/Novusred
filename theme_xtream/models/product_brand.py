from odoo import models, fields

class BrandType(models.Model):
    _name = 'brand.type'
    _description = 'Brand Type'

    name = fields.Char(string='Nombre de la marca', required=True)
    description = fields.Text(string='Descripción')

    icon_image = fields.Binary(
        string="Ícono del Producto",
        attachment=True,
        help="Sube un ícono representativo del producto."
    )
    cover_image = fields.Binary(
        string="Portada del Producto",
        attachment=True,
        help="Sube una imagen de portada para el producto."
    )
    active = fields.Boolean(
        string="Activo",
        default=True,
        help="Desactiva esta marca para que no se muestre en el carrusel."
    )