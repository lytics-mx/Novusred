from odoo import http
from odoo.http import request

class WebsiteSearch(http.Controller):

    @http.route('/search_redirect', auth='public', website=True)
    def search_redirect(self, search='', search_type='all', **kw):
        search = (search or '').strip()
        if not search:
            return request.redirect('/shop')

        # Si el usuario selecciona explícitamente
        if search_type == 'brand':
            return request.redirect('/brand_search?search=%s' % search)
        elif search_type == 'category':
            return request.redirect('/category_search?search=%s' % search)
        elif search_type == 'all':
            # 1. Buscar producto exacto
            product = request.env['product.template'].sudo().search([
                ('website_published', '=', True),
                ('name', 'ilike', search)
            ], limit=1)
            if product:
                # Redirige a la página del producto
                return request.redirect('/shop/product/%s' % product.id)

            # 2. Buscar marca
            brand = request.env['brand.type'].sudo().search([
                ('name', 'ilike', search)
            ], limit=1)
            if brand:
                return request.redirect('/brand_search?search=%s' % search)

            # 3. Buscar categoría
            category = request.env['product.category'].sudo().search([
                ('name', 'ilike', search)
            ], limit=1)
            if category:
                return request.redirect('/category_search?search=%s' % search)

            # 4. Si no encuentra nada, mostrar productos relacionados
            return request.redirect('/subcategory?search=%s' % search)
        else:
            return request.redirect('/subcategory?search=%s' % search)