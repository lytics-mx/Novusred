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
    state = fields.Selection([
        ('active', 'Activo'),
        ('inactive', 'Inactivo')
    ], string='Estado', default='inactive')
    is_active = fields.Boolean(string='Activo', default=False)
    
    def action_update_products(self):
        """Actualiza el campo free_shipping en los productos relacionados"""
        # Resetear todos los productos
        self.env['product.template'].sudo().search([]).write({'free_shipping': False})
        
        # Marcar los relacionados
        if self.product_ids:
            self.product_ids.write({'free_shipping': True})
        
        # Actualizar estado
        self.write({
            'state': 'active',
            'is_active': True
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Éxito',
                'message': f'Se han actualizado {len(self.product_ids)} productos con envío gratis',
                'sticky': False,
            }
        }
    
    def action_deactivate_products(self):
        """Desactiva el campo free_shipping en los productos relacionados"""
        # Desactivar los productos relacionados
        if self.product_ids:
            self.product_ids.write({'free_shipping': False})
        
        # Actualizar estado
        self.write({
            'state': 'inactive',
            'is_active': False
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Éxito',
                'message': f'Se han desactivado {len(self.product_ids)} productos de envío gratis',
                'sticky': False,
            }
        }
        
    def toggle_status(self):
        """Conmuta entre activo e inactivo"""
        if self.is_active:
            return self.action_deactivate_products()
        else:
            return self.action_update_products()