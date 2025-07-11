from odoo import models, fields

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_saved_for_later = fields.Boolean(string="Guardado para después", default=False)