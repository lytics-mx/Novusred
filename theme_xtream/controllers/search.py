from odoo import http
from odoo.http import request

class WebsiteSearch(http.Controller):
    @http.route('/search_redirect', auth='public', website=True)
    def search_redirect(self, search='', search_type='all'):
        Product = request.env['product.template'].sudo()
        # Buscar por default_code exacto
        product = Product.search([('default_code', '=', search)], limit=1)
        if not product:
            # Buscar por nombre exacto (case-insensitive)
            product = Product.search([('name', 'ilike', search)], limit=1)
        if product:
            # Use the website URL or fallback to product.id if slug is not available
            product_url = '/shop/product/%s' % product.id
            return request.redirect('%s?product=product.template(%s,)' % (product_url, product.id))

        if search_type == 'brand':
            return request.redirect('/brand_search_redirect?search=%s' % search)
        elif search_type == 'category':
            return request.redirect('/category_search?search=%s' % search)
        elif search_type == 'model':
            # Ya se intentó buscar por default_code y nombre arriba
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