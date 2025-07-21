from odoo import http
from odoo.http import request
import json


class WebsiteSearch(http.Controller):

    @http.route('/search_redirect', auth='public', website=True)
    def search_redirect(self, search='', search_type='all', **kw):
        Product = request.env['product.template'].sudo()
        # Buscar coincidencia exacta por nombre del producto
        product = Product.search([('name', '=', search)], limit=1)
        if product:
            # Redirigir directamente al producto específico en /shop/product/<product_id>
            return request.redirect('/shop/product/%s' % product.id)
        
        # Si no hay coincidencia exacta, manejar según el tipo de búsqueda
        if search_type == 'brand':
            return request.redirect('/brand_search_redirect?search=%s' % search.replace(' ', '-'))
        elif search_type == 'category':
            return request.redirect('/category_search?search=%s' % search.replace(' ', '-'))
        elif search_type == 'model':
            product = Product.search([('product_model', '=', search)], limit=1)
            if product:
                return request.redirect('/shop/product/%s' % product.id)
            else:
                return request.redirect('/subcategory?search=%s' % search.replace(' ', '-'))
        else:
            # Buscar si el texto coincide con una marca activa
            Brand = request.env['brand.type'].sudo()
            brand = Brand.search([('name', 'ilike', search), ('active', '=', True)], limit=1)
            if brand:
                return request.redirect('/subcategory?brand_id=%s' % brand.id)
            # Si no es marca, buscar si coincide con una categoría
            Category = request.env['product.category'].sudo()
            category = Category.search([('name', 'ilike', search)], limit=1)
            if category:
                return request.redirect('/subcategory?category_id=%s' % category.id)
            # Si no es marca ni categoría, redirigir a subcategory con search
            return request.redirect('/subcategory?search=%s' % search.replace(' ', '-'))

    @http.route('/search_live', type='http', auth='public', website=True)
    def search_live(self, query):
        # Buscar productos por nombre o modelo
        products = request.env['product.template'].sudo().search([
            '|',  # Condición OR
            ('name', 'ilike', query),
            ('product_model', 'ilike', query)
        ], limit=10)
        
        results = [{
            'id': product.id,
            'name': product.name,
            'price': product.list_price,
        } for product in products]
        
        return request.make_response(json.dumps({'results': results}), headers=[('Content-Type', 'application/json')])