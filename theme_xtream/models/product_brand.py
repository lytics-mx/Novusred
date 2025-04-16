from odoo import models, fields,api

class BrandType(models.Model):
    _name = 'brand.type'
    _description = 'Brand Type'

    name = fields.Char(string='Nombre de la marca', required=True)
    description = fields.Text(string='Descripción')

    
    product_count = fields.Integer(
        string="Cantidad de Productos",
        compute="_compute_product_count",
        store=True
    )

    @api.depends('product_tmpl_ids')
    def _compute_product_count(self):
        for category in self:
            category.product_count = len(category.product_tmpl_ids)