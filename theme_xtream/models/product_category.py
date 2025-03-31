from odoo import models, fields

class ProductCategory(models.Model):
    _inherit = 'product.category'

    icon = fields.Binary(string="Category Icon")  # Campo para subir el ícono
    is_visible_in_menu = fields.Boolean(string="Visible", default=False)  # Campo booleano para habilitar visibilidad


    @classmethod
    def get_visible_categories(cls):
        """Obtiene las categorías principales y subcategorías visibles."""
        categories = cls.env['product.category'].search([('is_visible_in_menu', '=', True), ('parent_id', '=', False)])
        result = []
        for category in categories:
            result.append({
                'name': category.name,
                'subcategories': [
                    {'name': subcategory.name}
                    for subcategory in category.child_id.filtered(lambda c: c.is_visible_in_menu)
                ]
            })
        return result