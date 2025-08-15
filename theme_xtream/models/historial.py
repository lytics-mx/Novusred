from odoo import models, fields, api

class ProductViewHistory(models.Model):
    _name = 'product.view.history'
    _description = 'Historial de productos vistos'

    user_id = fields.Many2one('res.users', string="Usuario", required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string="Producto", required=True, ondelete='cascade')
    viewed_at = fields.Datetime(string="Visto en", default=fields.Datetime.now)

    @api.model
    def add_product_to_history(self, product_id):
        """Agrega un producto al historial del usuario actual solo si es usuario portal."""
        user = self.env.user
        portal_group = self.env.ref('base.group_portal')
        if user.id and portal_group in user.groups_id:
            self.create({
                'user_id': user.id,
                'product_id': product_id,
            })