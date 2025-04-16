from odoo import models, fields

class BrandType(models.Model):
    _name = 'brand.type'
    _description = 'Brand Type'

    name = fields.Char(string='Nombre de la marca', required=True)
    description = fields.Text(string='Descripción')