from odoo import models, fields

class SavedItems(models.Model):
    _name = 'saved.items'
    _description = 'Productos Guardados para Después'

    user_id = fields.Many2one('res.users', string='Usuario', required=True)
    product_id = fields.Many2one('product.product', string='Producto', required=True)
    name = fields.Char(string='Nombre del Producto')
    price = fields.Float(string='Precio')
    brand_name = fields.Char(string='Marca')
    brand_id = fields.Many2one('brand.type', string='Tipo de Marca')  # Cambiado a brand.type
    quantity_available = fields.Float(string='Cantidad Disponible')