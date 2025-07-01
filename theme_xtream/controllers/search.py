from odoo import http
from odoo.http import request

class WebsiteSearch(http.Controller):

    @http.route('/search_redirect', auth='public', website=True)
    def search_redirect(self, search='', search_type='all', **kw):
        if search_type == 'brand':
            return request.redirect('/brand_search_redirect?search=%s' % search)
        elif search_type == 'category':
            return request.redirect('/category_search?search=%s' % search)
        elif search_type == 'model':
            Product = request.env['product.template'].sudo()
            product = Product.search([('default_code', '=', search)], limit=1)
            if product:
                return request.redirect('/shop/%s?product=product.template(%s,)' % (product.slug(), product.id))
            else:
                return request.redirect('/subcategory?search=%s' % search)
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
            return request.redirect('/subcategory?search=%s' % search)
        
    @http.route('/search_suggestions', type='json', auth='public', methods=['GET'])
    def search_suggestions(self, query):
        products = http.request.env['product.template'].search([('name', 'ilike', query)], limit=5)
        return [{'name': p.name, 'price': p.list_price, 'image': f'/web/image/product.template/{p.id}/image_1920'} for p in products]        