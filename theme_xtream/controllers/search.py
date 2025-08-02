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
        Product = request.env['product.template'].sudo()

        # 1. Buscar por nombre exacto de producto (prioridad máxima)
        product = Product.search([('name', 'ilike', search)], limit=1, order='name')
        if product and product.name.lower().startswith(search.lower()):
            return request.redirect(f'/shop/{product.slug()}?product=product.template({product.id},)')

        # 2. Buscar por modelo exacto
        product_model = Product.search([('product_model', '=', search)], limit=1)
        if product_model:
            return request.redirect(f'/shop/{product_model.slug()}?product=product.template({product_model.id},)')

        # 3. Buscar por marca
        Brand = request.env['brand.type'].sudo()
        brand = Brand.search([('name', 'ilike', search), ('active', '=', True)], limit=1)
        if brand:
            return request.redirect(f'/subcategory?brand_id={brand.id}')

        # 4. Buscar por categoría
        Category = request.env['product.category'].sudo()
        category = Category.search([('name', 'ilike', search)], limit=1)
        if category:
            return request.redirect(f'/subcategory?category_id={category.id}')

        # 5. Si no se encuentra nada, redirigir a subcategoría con búsqueda
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
            'name': product.name.replace(' ', '-'),
            'price': product.list_price,
        } for product in products]

        return request.make_response(json.dumps({'results': results}), headers=[('Content-Type', 'application/json')])