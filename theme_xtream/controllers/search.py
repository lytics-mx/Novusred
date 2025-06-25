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

        # Si es modelo o nombre de producto, mostrar primero subcategory si hay similares
        if search_type == 'model' or (not product and search):
            # Buscar productos similares por nombre
            similar_products = Product.search([('name', 'ilike', search)], limit=5)
            if similar_products:
                # Redirigir primero a subcategory mostrando similares, luego al producto real si existe
                # Usar un template que haga el redirect automático después de 1 segundo
                return request.render('theme_xtream.subcategory_redirect', {
                    'search': search,
                    'product': product,
                    'similar_products': similar_products,
                    'redirect_url': '/shop/product/%s?product=product.template(%s,)' % (product.id, product.id) if product else '',
                })

        if product:
            product_url = '/shop/product/%s' % product.id
            return request.redirect('%s?product=product.template(%s,)' % (product_url, product.id))

        if search_type == 'brand':
            return request.redirect('/brand_search_redirect?search=%s' % search)
        elif search_type == 'category':
            return request.redirect('/category_search?search=%s' % search)
        elif search_type == 'model':
            return request.redirect('/subcategory?search=%s' % search)
        else:
            Brand = request.env['brand.type'].sudo()
            brand = Brand.search([('name', 'ilike', search), ('active', '=', True)], limit=1)
            if brand:
                return request.redirect('/subcategory?brand_id=%s' % brand.id)
            Category = request.env['product.category'].sudo()
            category = Category.search([('name', 'ilike', search)], limit=1)
            if category:
                return request.redirect('/subcategory?category_id=%s' % category.id)
            return request.redirect('/subcategory?search=%s' % search)