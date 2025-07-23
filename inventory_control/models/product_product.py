from odoo import models, api, fields 

class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    product_model = fields.Char('Modelo de producto', related='product_tmpl_id.product_model', store=True)

    @api.onchange('product_tmpl_id')
    def _onchange_product_tmpl_id(self):
        if self.product_tmpl_id:
            self.product_model = self.product_tmpl_id.product_model
            
    @api.onchange('product_model')
    def _onchange_product_model(self):
        if self.product_tmpl_id:
            self.product_tmpl_id.product_model = self.product_model

    @api.model
    def create(self, vals):
        res = super(ProductProduct, self).create(vals)
        # Sincronizar el model de la plantilla cuando se crea la variante
        if 'product_model' in vals and res.product_tmpl_id:
            res.product_tmpl_id.write({'product_model': vals['product_model']})
        return res
    
    def write(self, vals):
        res = super(ProductProduct, self).write(vals)
        # Sincronizar solo si el cambio no vino del template
        if 'product_model' in vals and not self.env.context.get('template_update'):
            self.product_tmpl_id.with_context(product_variant_update=True).write({'product_model': vals['product_model']})
        return res

    def name_get(self):
        result = []
        for product in self:
            # Mostrar primero el modelo y luego el nombre del producto
            name = f"{product.product_model or ''} - {product.name or ''}"
            result.append((product.id, name))
        return result
    
    def _search(self, args, offset=0, limit=None, order=None, count=False):
        # Priorizar búsqueda por modelo y nombre
        order = order or 'product_model, name'
        return super(ProductProduct, self)._search(args, offset=offset, limit=limit, order=order, count=count)

    @property
    def display_name(self):
        # Mostrar primero el modelo y luego el nombre del producto
        return f"{self.product_model or ''} - {self.name or ''}"   