from odoo import models, fields, api

class ProductViewHistory(models.Model):
    _name = 'product.view.history'
    _description = 'Historial de productos vistos'

    user_id = fields.Many2one('res.users', string="Usuario", required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string="Producto", required=True, ondelete='cascade')
    viewed_at = fields.Datetime(string="Visto en", default=fields.Datetime.now)
    url = fields.Char(string="URL")  # Nuevo campo para guardar el URL