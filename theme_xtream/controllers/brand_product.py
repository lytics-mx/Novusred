from odoo import http
from odoo.http import request

class WebsiteBrand(http.Controller):

    @http.route('/brand/<string:brand_type>', auth='public', website=True)
    def brand_products(self, brand_type):
        BrandType = request.env['brand.type']
        brand_type_rec = BrandType.sudo().search([('slug', '=', brand_type)], limit=1)
        if not brand_type_rec:
            return request.not_found()

        products = request.env['product.template'].sudo().search([('brand_type_id', '=', brand_type_rec.id)])

        return request.render('theme_xtream.website_brand', {
            'brand_type': brand_type_rec,
            'products': products,
        })

    @http.route('/brand', auth='public', website=True)
    def home(self):
        # Mostrar productos normales si no hay marca seleccionada
        products = request.env['product.template'].sudo().search([('website_published', '=', True)], order='create_date desc', limit=10)
        return http.request.render('theme_xtream.website_brand', {
            'products': products,
        })