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
        """Activa o desactiva el envío gratis en los productos relacionados"""
        # Verificar si los productos seleccionados ya tienen free_shipping activo
        if self.product_ids and all(self.product_ids.mapped('free_shipping')):
            # Si todos tienen activo, desactivar
            self.product_ids.write({'free_shipping': False})
            message = f"Se desactivaron {len(self.product_ids)} productos de envío gratis."
        else:
            # Si alguno no tiene activo, activar
            self.product_ids.write({'free_shipping': True})
            message = f"Se activaron {len(self.product_ids)} productos de envío gratis."

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Resultado',
                'message': message,
                'sticky': False,
            }
        }