import logging
from odoo import models, fields, api
import re

_logger = logging.getLogger(__name__)

class ProductCategory(models.Model):
    _inherit = 'product.category'

    icon = fields.Binary(string="Category Icon")  # Campo para subir el ícono
    is_visible_in_menu = fields.Boolean(string="Visible", default=False)  # Campo booleano para habilitar visibilidad
    banner_image = fields.Binary(string="Imagen de Banner")  # <-- Nuevo campo para banner
    slug = fields.Char('Slug', index=True)

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
    
    def get_visible_categories(self):
        """Obtiene las categorías principales y subcategorías visibles."""
        categories = self.env['product.category'].search([('is_visible_in_menu', '=', True), ('parent_id', '=', False)])
        result = []
        for category in categories:
            result.append({
                'name': category.name,
                'subcategories': [
                    {'name': subcategory.name}
                    for subcategory in category.child_id.filtered(lambda c: c.is_visible_in_menu)
                ]
            })
        # Agrega un log para verificar los datos
        _logger.info(f"Visible Categories: {result}")
        return result
    
