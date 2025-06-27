from odoo import models, fields

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    public = fields.Boolean(string="Public", default=True)