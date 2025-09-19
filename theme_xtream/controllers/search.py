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

        # Buscar el primer producto que coincida con el nombre o modelo
        product = Product.search([
            '|',
            ('name', 'ilike', search),
            ('product_model', 'ilike', search)
        ], limit=1)

        # Si se encuentra un producto, redirigir a su página usando website_url
        if product and product.website_url:
            return request.redirect(product.website_url)

        # Si no se encuentra ningún producto, redirigir a la búsqueda general
        if search_type == 'brand':
            return request.redirect(f'/brand_search_redirect?search={search_sanitized}')
        elif search_type == 'category':
            return request.redirect(f'/category_search?search={search_sanitized}')
        elif search_type == 'model':
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

        product_template = request.env['product.template'].sudo()

        # 1) Buscar por código de producto (default_code empieza con query)
        products = product_template.search(
            [('default_code', '=ilike', query_sanitized + '%')],
            order='list_price asc',
            limit=10
        )

        # 2) Si no hubo resultados, buscar por nombre o modelo (empieza con query)
        if not products:
            products = product_template.search(
                ['|',
                 ('name', '=ilike', query_sanitized + '%'),
                 ('product_model', '=ilike', query_sanitized + '%')],
                order='list_price asc',
                limit=10
            )

        results = [{
            'id': product.id,
            'name': product.name.replace(' ', '-'),
            'price': product.list_price,
        } for product in products]
        
        return request.make_response(json.dumps({'results': results}), headers=[('Content-Type', 'application/json')])