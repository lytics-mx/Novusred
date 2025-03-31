import logging
from odoo import models, fields

_logger = logging.getLogger(__name__)

class ProductCategory(models.Model):
    _inherit = 'product.category'

    icon = fields.Binary(string="Category Icon")  # Campo para subir el ícono
    is_visible_in_menu = fields.Boolean(string="Visible", default=False)  # Campo booleano para habilitar visibilidad

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