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
        # PRIMERO: Desactiva el envío gratis en TODOS los productos
        self.env['product.template'].sudo().search([]).write({'free_shipping': False})
        
        # SEGUNDO: Activa SOLO los productos en este modelo
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
    
    @api.model
    def init(self):
        """Se ejecuta al iniciar el servidor"""
        # Buscar el registro activo de free.shipping
        shipping_record = self.search([], limit=1)
        if shipping_record:
            # Desactivar en todos
            self.env['product.template'].sudo().search([]).write({'free_shipping': False})
            # Activar solo en los relacionados
            if shipping_record.product_ids:
                shipping_record.product_ids.write({'free_shipping': True})    