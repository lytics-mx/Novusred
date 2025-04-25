from odoo import models, fields

class WebsiteTrack(models.Model):
    _inherit = 'website.track'

    hidden = fields.Boolean(string="Oculto en el historial", default=False)