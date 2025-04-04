from odoo import http
from odoo.http import request

class WebsiteBrand(http.Controller):

    @http.route(['/brand/products'], type='json', auth="public", website=True)
    def filter_products(self, tag_ids=None):
        domain = [('website_published', '=', True)]
        if tag_ids:
            domain.append(('tag_ids', 'in', tag_ids))
        
        products = request.env['product.template'].sudo().search(domain)
        products_data = []
        for product in products:
            products_data.append({
                'id': product.id,
                'name': product.name,
                'price': request.env['ir.qweb.field.monetary'].value_to_html(
                    product.list_price, {'display_currency': request.env.company.currency_id}),
                'image': product.image_1920 and f"data:image/png;base64,{product.image_1920.decode('utf-8')}" or None,
            })
        return products_data