from odoo import models, fields
from datetime import date

class WebsiteTrack(models.Model):
    _inherit = 'website.track'

    def get_grouped_viewed_products(self):
        """Agrupa los productos vistos por 'Hoy' y por mes."""
        grouped_products = {'Hoy': [], 'Enero': [], 'Febrero': [], 'Marzo': [], 'Abril': [], 'Mayo': []}
        today = date.today()

        viewed_products = self.env['website.track'].sudo().search([
            ('visitor_id.partner_id', '=', self.env.user.partner_id.id),
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