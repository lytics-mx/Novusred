from odoo import models, fields

class ProductViewHistory(models.Model):
    _name = 'product.view.history'
    _description = 'Historial de Productos Vistos'

    user_id = fields.Many2one('res.users', string='Usuario', required=True)
    product_id = fields.Many2one('product.template', string='Producto', required=True)
    viewed_at = fields.Datetime(string='Visto el', default=fields.Datetime.now)
    purchased = fields.Boolean(string='Comprado', default=False)

    @api.model
    def add_product_to_history(self, product_id):
        """Agrega un producto al historial del usuario actual."""
        if self.env.user.id:
            self.create({
                'user_id': self.env.user.id,
                'product_id': product_id,
            })