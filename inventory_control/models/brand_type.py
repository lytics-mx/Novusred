from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re

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
        'product_tmpl_id',  # CAMBIAR: de 'product_id' a 'product_tmpl_id'
        string="Productos Relacionados",
        help="Selecciona hasta 3 productos relacionados a esta marca."
    )
    slug = fields.Char(string='Slug', required=True, index=True)

    @api.onchange('name')
    def _onchange_name_slug(self):
        if self.name:
            # Genera un slug amigable para URL
            slug = self.name.lower()
            slug = re.sub(r'[^a-z0-9]+', '-', slug)
            slug = slug.strip('-')
            self.slug = slug

    @api.model
    def create(self, vals):
        if 'name' in vals and not vals.get('slug'):
            slug = vals['name'].lower()
            slug = re.sub(r'[^a-z0-9]+', '-', slug)
            slug = slug.strip('-')
            vals['slug'] = slug
        return super().create(vals)

    def write(self, vals):
        if 'name' in vals and not vals.get('slug'):
            slug = vals['name'].lower()
            slug = re.sub(r'[^a-z0-9]+', '-', slug)
            slug = slug.strip('-')
            vals['slug'] = slug
        return super().write(vals)
    
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