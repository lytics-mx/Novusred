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
    
    def action_toggle_free_shipping(self):
        """Activa o desactiva el envío gratis en los productos relacionados"""
        # Desactiva el envío gratis en TODOS los productos
        self.env['product.template'].sudo().search([]).write({'free_shipping': False})
        
        # Activa SOLO los productos en este modelo
        if self.product_ids:
            self.product_ids.write({'free_shipping': True})
            message = f"Se activaron {len(self.product_ids)} productos de envío gratis."
        else:
            message = "No hay productos seleccionados para envío gratis."
    
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Resultado',
                'message': message,
                'sticky': False,
            }
        }