
from odoo import models, fields
from odoo.exceptions import ValidationError


class ProductName(models.Model):
    _name = 'product.namemodel'
    _description = 'Nombre del modelo'

    name_model = fields.Char(string='Nombre', required=True, unique=True)                              