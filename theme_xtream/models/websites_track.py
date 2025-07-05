from odoo import models, fields, api
from datetime import date

class WebsiteTrack(models.Model):
    _inherit = 'website.track'
    
    # Add direct user relationship field
    user_id = fields.Many2one('res.users', string='Viewing User', readonly=True)
    
    @api.model
    def create(self, vals):
        # When creating a track record, set the current user if they're logged in
        if not self.env.user._is_public():
            vals['user_id'] = self.env.user.id
        return super(WebsiteTrack, self).create(vals)
    
    def get_grouped_viewed_products(self):
        """Agrupa los productos vistos por 'Hoy' y por mes."""
        grouped_products = {'Hoy': [], 'Enero': [], 'Febrero': [], 'Marzo': [], 'Abril': [], 'Mayo': []}
        today = date.today()

        # Query using the direct user_id relationship instead of visitor
        viewed_products = self.env['website.track'].sudo().search([
            ('user_id', '=', self.env.user.id),  # Use direct user relationship
            ('product_id', '!=', False)
        ], order='id desc').mapped('product_id.product_tmpl_id').filtered(lambda p: p.website_published)

        for product in viewed_products:
            last_viewed_date = product.last_viewed_date
            if last_viewed_date:
                if last_viewed_date.date() == today:
                    grouped_products['Hoy'].append(product)
                else:
                    month_name = last_viewed_date.strftime('%B')
                    grouped_products[month_name].append(product)

        return grouped_products