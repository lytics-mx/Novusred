from odoo import models, fields, api
from datetime import datetime, timezone

class ProductViewHistory(models.Model):
    _name = 'product.view.history'
    _description = 'Historial de productos vistos'

    user_id = fields.Many2one('res.users', string="Usuario", required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string="Producto", required=True, ondelete='cascade')
    viewed_at = fields.Datetime(string="Visto en", default=fields.Datetime.now)

    @api.model
    def add_product_to_history(self, product_id):
        """Agrega un producto al historial del usuario actual."""
        if self.env.user.id:
            self.create({
                'user_id': self.env.user.id,
                'product_id': product_id,
            })