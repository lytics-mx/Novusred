from odoo import models, api, fields

class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    product_model = fields.Char('Modelo de producto')

    @api.onchange('product_tmpl_id')
    def _onchange_product_tmpl_id(self):
        if self.product_tmpl_id:
            self.product_model = self.product_tmpl_id.product_model
            
    @api.onchange('product_model')
    def _onchange_product_model(self):
        if self.product_tmpl_id:
            self.product_tmpl_id.product_model = self.product_model