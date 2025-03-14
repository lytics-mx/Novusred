from odoo import models, fields, api

class ProductProduct(models.Model):

    _inherit = 'product.product'

    qty_available = fields.Float(string="Cantidad a la mano", compute='_compute_qty_available', store=True)

    @api.model
    def create(self, vals):
        # Lógica cuando se crea un nuevo producto
        res = super(ProductProduct, self).create(vals)
        # Crear stock_quant para este nuevo producto si es necesario
        self.create_quant_for_product(res)
        return res

    def create_quant_for_product(self, product):
        # Esto podría ser mejorado según los requisitos específicos
        quant_obj = self.env['stock.quant']
        for location in self.env['stock.location'].search([]):
            quant_obj.create({
                'product_id': product.id,
                'location_id': location.id,
                'quantity': product.qty_available,  # O ajusta según lo que sea necesario
            })

    @api.onchange('qty_available')
    def _onchange_qty_available(self):
        for product in self:
            # Actualizar stock_quant con la cantidad a la mano
            quant_records = self.env['stock.quant'].search([('product_id', '=', product.id)])
            for quant in quant_records:
                quant.write({'quantity': product.qty_available})