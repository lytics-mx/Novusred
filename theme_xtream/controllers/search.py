from odoo import http
from odoo.http import request
import json


class WebsiteSearch(http.Controller):

    def _sanitize_search(self, search):
        # Reemplaza espacios por guiones
        return search.replace(' ', '-')

    @http.route('/search_redirect', auth='public', website=True)
    def search_redirect(self, search='', search_type='all', **kw):
        search_sanitized = self._sanitize_search(search)
        if search_type == 'brand':
            return request.redirect(f'/brand_search_redirect?search={search_sanitized}')
        elif search_type == 'category':
            return request.redirect(f'/category_search?search={search_sanitized}')
        elif search_type == 'model':
            Product = request.env['product.template'].sudo()
            product = Product.search([('product_model', '=', search)], limit=1)
            if product:
                return request.redirect(f'/shop/{product.slug()}?product=product.template({product.id},)')
            else:
                return request.redirect(f'/subcategory?search={search_sanitized}')
        else:
            Brand = request.env['brand.type'].sudo()
            brand = Brand.search([('name', 'ilike', search), ('active', '=', True)], limit=1)
            if brand:
                return request.redirect(f'/subcategory?brand_id={brand.id}')
            Category = request.env['product.category'].sudo()
            category = Category.search([('name', 'ilike', search)], limit=1)
            if category:
                return request.redirect(f'/subcategory?category_id={category.id}')
            return request.redirect(f'/subcategory?search={search_sanitized}')

    @http.route('/search_live', type='http', auth='public', website=True)
    def search_live(self, query):
        query_sanitized = self._sanitize_search(query)
        products = request.env['product.template'].sudo().search([
            '|',
            ('name', 'ilike', query),
            ('product_model', 'ilike', query)
        ], limit=10)

        results = [{
            'id': product.id,
            'name': product.name,  # <-- Mostrar el nombre original
            'price': product.list_price,
        } for product in products]

        return request.make_response(json.dumps({'results': results}), headers=[('Content-Type', 'application/json')])