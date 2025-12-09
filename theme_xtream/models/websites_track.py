from odoo import models, fields, api
from datetime import date

class WebsiteTrack(models.Model):
    _inherit = 'website.track'
    
    # Add direct user relationship field
    user_id = fields.Many2one('res.users', string='Viewing User', readonly=True)
    
    @api.model
    def create(self, vals):
        # Prefer explicit user_id passed in vals
        if vals.get('user_id'):
            return super(WebsiteTrack, self).create(vals)

        # Prefer user id passed in context (tracking_user_id)
        tracking_user = self.env.context.get('tracking_user_id')
        if tracking_user:
            vals['user_id'] = tracking_user
        else:
            # Fallback: si el env.user actual no es public, asignarlo
            if not self.env.user._is_public():
                vals['user_id'] = self.env.user.id

        return super(WebsiteTrack, self).create(vals)
    
    
    def get_grouped_viewed_products(self, user_id=None):
        """Agrupa los productos vistos por 'Hoy' y por mes para un usuario específico."""
        grouped_products = {'Hoy': [], 'Enero': [], 'Febrero': [], 'Marzo': [], 'Abril': [], 'Mayo': []}
        today = date.today()
    
        # Use the provided user_id or fall back to current user
        target_user_id = user_id if user_id else self.env.user.id
    
        # Query using the direct user_id relationship
        viewed_products = self.env['website.track'].sudo().search([
            ('user_id', '=', target_user_id),  # Use the target user
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