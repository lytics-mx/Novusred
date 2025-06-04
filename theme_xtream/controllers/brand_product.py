from odoo import http
from odoo.http import request
import urllib.parse
import re

class WebsiteBrand(http.Controller):

    @http.route('/brand/<string:brand_name>', auth='public', website=True)
    def brand_products(self, brand_name):
        BrandType = request.env['brand.type']
        # Busca el slug en minúsculas para que coincida siempre
        brand_type_rec = BrandType.sudo().search([
            ('slug', '=', brand_name.lower()),
            ('active', '=', True)
        ], limit=1)
        if not brand_type_rec:
            return request.not_found()

        products = request.env['product.template'].sudo().search([
            ('brand_type_id', '=', brand_type_rec.id),
            ('website_published', '=', True)
        ])
        # Obtén todas las categorías de los productos de la marca
        category_ids = products.mapped('categ_id').ids
        categories = request.env['product.category'].sudo().browse(category_ids)
        child_categories = categories.mapped('child_id')
        
        return request.render('theme_xtream.brand_search', {
            'brand_type': brand_type_rec,
            'products': products,
            'categories': categories,
            'child_categories': child_categories,
        })

    @http.route('/brand_search_redirect', type='http', auth='public', website=True)
    def brand_search_redirect(self, search=None, **kwargs):
        if search:
            BrandType = request.env['brand.type'].sudo()
            # Primero busca coincidencia exacta (insensible a mayúsculas)
            brand = BrandType.search([('name', '=', search)], limit=1)
            if not brand:
                # Si no hay coincidencia exacta, busca parcial
                brand = BrandType.search([('name', 'ilike', search)], limit=1)
            if brand:
                brand_name_url = brand.slug
                return request.redirect('/brand/%s' % brand_name_url)
        return request.redirect('/brand')

    @http.route('/brand', auth='public', website=True)
    def home(self):
        products = request.env['product.template'].sudo().search([('website_published', '=', True)], order='create_date desc', limit=10)
        return http.request.render('theme_xtream.website_brand', {
            'products': products,
        })
    
