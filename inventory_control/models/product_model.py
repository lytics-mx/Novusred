
from odoo import models, fields


class ProductModel(models.Model):
    _name = 'product.model'
    _description = 'Nombre del Modelo de Producto'

    name = fields.Char(string='Nombre del Modelo', required=True, unique=True)