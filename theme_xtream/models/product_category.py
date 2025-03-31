from odoo import models, fields

class ProductCategory(models.Model):
    _inherit = 'product.category'

    icon = fields.Binary(string="Category Icon")  # Campo para subir el ícono
    is_visible_in_menu = fields.Boolean(string="Visible")  # Campo booleano para habilitar visibilidad