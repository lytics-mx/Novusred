from odoo import fields, models, api, tools, _
class Prueba(models.Model):
    _name = 'prueba'
    _description = 'prueba'

    name = fields.Char(string='Name', required=True)