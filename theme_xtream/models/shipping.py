from odoo import models, fields

class FreeShippingCampaign(models.Model):
    _name = 'free.shipping.campaign'
    _description = 'Campaña de Envío Gratis'

    name = fields.Char(string="Nombre de la campaña", required=True)
    active = fields.Boolean(string="Activo", default=True)
    start_date = fields.Date(string="Fecha de inicio")
    end_date = fields.Date(string="Fecha de fin")
    product_ids = fields.Many2many('product.template', string="Productos con Envío Gratis")
    notes = fields.Text(string="Notas")