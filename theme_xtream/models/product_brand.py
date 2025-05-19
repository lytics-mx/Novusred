from odoo import models, fields, api
from odoo.exceptions import ValidationError

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

    product_ids = fields.Many2many(
        'product.template',
        'brand_type_product_rel',
        'brand_type_id',
        'product_id',
        string="Productos Relacionados",
        domain="[('brand_type_id', '=', id)]",
        help="Selecciona hasta 3 productos relacionados a esta marca."
    )

    @api.onchange('product_ids')
    def _onchange_product_ids_limit(self):
        if self.product_ids and len(self.product_ids) > 3:
            self.product_ids = self.product_ids[:3]
            return {
                'warning': {
                    'title': "Límite de productos",
                    'message': "Solo puedes seleccionar hasta 3 productos relacionados."
                }
            }