from odoo import http
from odoo.http import request

class WebsiteSale(http.Controller):
    @http.route(['/shop'], type='http', auth="public", website=True)
    def shop(self, brand=None, **kwargs):
        domain = []
        if brand:
            domain.append(('brand_type_id', '=', int(brand)))
        products = request.env['product.template'].search(domain)
        brands = request.env['brand.type'].search([])
        return request.render('website_sale.products', {
            'products': products,
            'brands': brands,
            'selected_brand': int(brand) if brand else None,
        })