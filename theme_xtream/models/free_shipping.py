from odoo import models, fields

class ShoppingFree(models.Model):
    _name = 'shopping.free'
    _description = 'Shopping Free'

    name = fields.Char(string='Nombre', required=True)
    product_ids = fields.Many2many(
        'product.template',
        string='Productos Relacionados',
        help='Selecciona los productos relacionados'
    )