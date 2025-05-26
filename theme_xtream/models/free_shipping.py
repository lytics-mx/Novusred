from odoo import models, fields, api

class ShoppingFree(models.Model):
    _name = 'free.shipping'
    _description = 'Free Shipping'

    name = fields.Char(string='Nombre', required=True)
    product_ids = fields.Many2many(
        'product.template',
        string='Productos Relacionados',
        help='Selecciona los productos relacionados'
    )
    
    def action_update_products(self):
        """Actualiza el campo free_shipping en los productos relacionados"""
        # Resetear todos los productos
        self.env['product.template'].sudo().search([]).write({'free_shipping': False})
        
        # Marcar los relacionados
        if self.product_ids:
            self.product_ids.write({'free_shipping': True})
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Éxito',
                'message': f'Se han actualizado {len(self.product_ids)} productos con envío gratis',
                'sticky': False,
            }
        }
    
