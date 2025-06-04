from odoo import http
from odoo.http import request
import urllib.parse

class WebsiteBrand(http.Controller):

    @http.route('/brand/<string:brand_name>', auth='public', website=True)
    def brand_products(self, brand_name):
        BrandType = request.env['brand.type']
        brand_type_rec = BrandType.sudo().search([('name', 'ilike', brand_name)], limit=1)
        if not brand_type_rec:
            return request.not_found()

        products = request.env['product.template'].sudo().search([('brand_type_id', '=', brand_type_rec.id)])

        return request.render('theme_xtream.brand_search', {
            'brand_type': brand_type_rec,
            'products': products,
        })
    
    @http.route('/brand_search_redirect', type='http', auth='public', website=True)
    def brand_search_redirect(self, search=None, **kwargs):
        if search:
            brand = request.env['brand.type'].sudo().search([('name', 'ilike', search)], limit=1)
            if brand:
                # Codifica el name para la URL
                brand_name_url = urllib.parse.quote(brand.name)
                return request.redirect('/brand/%s' % brand_name_url)
        return request.redirect('/brand')   

    @http.route('/brand', auth='public', website=True)
    def home(self):
        products = request.env['product.template'].sudo().search([('website_published', '=', True)], order='create_date desc', limit=10)
        return http.request.render('theme_xtream.website_brand', {
            'products': products,
        })