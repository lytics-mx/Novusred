from odoo import http
from odoo.http import request

class WebsiteBrand(http.Controller):

    @http.route('/brand/<string:brand_type>', auth='public', website=True)
    def brand_products(self, brand_type):
        # Buscar el tipo de marca por el campo 'slug' o 'name'
        BrandType = request.env['brand.type']
        brand_type_rec = BrandType.sudo().search([('slug', '=', brand_type)], limit=1)
        if not brand_type_rec:
            return request.not_found()

        # Buscar productos que coincidan con ese tipo de marca
        products = request.env['product.template'].sudo().search([('brand_type_id', '=', brand_type_rec.id)])

        # Renderizar el template con los productos y el tipo de marca
        return request.render('theme_xtream.website_brand', {
            'brand_type': brand_type_rec,
            'products': products,
        })
    
    @http.route('/brand', auth='public', website=True)
    def home(self):
        return http.request.render('theme_xtream.website_brand')  