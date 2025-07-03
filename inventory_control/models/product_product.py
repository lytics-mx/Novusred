from odoo import models, api, fields

class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    product_model = fields.Char('Modelo de producto')

    @api.model
    def sync_product_model_and_default_code_from_templates(self):
        """
        Replica los valores de los campos `product_model` y `default_code` desde `product.template` 
        hacia todas las variantes `product.product`, sin sobrescribir valores existentes.
        """
        self.env.cr.execute("""
            UPDATE product_product pp
            SET product_model = COALESCE(pp.product_model, pt.product_model),
                default_code = COALESCE(pp.default_code, pt.default_code)
            FROM product_template pt
            WHERE pp.product_tmpl_id = pt.id
              AND (pt.product_model IS NOT NULL OR pt.default_code IS NOT NULL)
        """)
        
        updated_count = self.env.cr.rowcount
        self.env.cr.commit()
        
        return {
            'status': 'success',
            'fields_updated': updated_count
        }
