from odoo import models, fields

class BrandType(models.Model):
    _name = 'brand.type'
    _description = 'Brand Type'

    name = fields.Char(string='Nombre de la marca', required=True)
    description = fields.Text(string='Descripción')

    
    product_count = fields.Integer(
            string="Cantidad de Productos",
            compute="_compute_product_count"
        )
    
    def _compute_product_count(self):
        for brand in self:
            brand.product_count = self.env['product.template'].search_count([('brand_type_id', '=', brand.id)])   