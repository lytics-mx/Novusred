from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def get_compras(self):
        """Obtiene los productos entregados para el usuario actual."""
        user_id = self.env.user.id
        delivered_pickings = self.search([
            ('state', '=', 'done'),  # Solo entregas completadas
            ('partner_id', '=', user_id)  # Filtrar por usuario actual
        ])
        return delivered_pickings