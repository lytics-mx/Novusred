from odoo import http
from odoo.http import request
import json


class WebsiteSearch(http.Controller):

    @http.route('/search_redirect', auth='public', website=True)
    def search_redirect(self, search='', search_type='all', **kw):
        # Reemplazar guiones por espacios para la búsqueda
        search_clean = search.replace('-', ' ')
        if search_type == 'brand':
            return request.redirect('/brand_search_redirect?search=%s' % search)
        elif search_type == 'category':
            return request.redirect('/category_search?search=%s' % search)
        elif search_type == 'model':
            Product = request.env['product.template'].sudo()
            product = Product.search([('product_model', '=', search_clean)], limit=1)
            if product:
                return request.redirect('/shop/%s?product=product.template(%s,)' % (product.slug(), product.id))
            else:
                return request.redirect('/subcategory?search=%s' % search)
        else:
            # Buscar si el texto coincide con una marca activa
            Brand = request.env['brand.type'].sudo()
            brand = Brand.search([('name', 'ilike', search_clean), ('active', '=', True)], limit=1)
            if brand:
                return request.redirect('/subcategory?brand_id=%s' % brand.id)
            # Si no es marca, buscar si coincide con una categoría
            Category = request.env['product.category'].sudo()
            category = Category.search([('name', 'ilike', search_clean)], limit=1)
            if category:
                return request.redirect('/subcategory?category_id=%s' % category.id)
            # Si no es marca ni categoría, redirigir a subcategory con search
            return request.redirect('/subcategory?search=%s' % search)
        

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