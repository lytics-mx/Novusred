from odoo import http
from odoo.http import request

class SearchRedirectController(http.Controller):

    @http.route('/search_redirect', auth='public', website=True)
    def search_redirect(self, search=None, **kwargs):
        if not search:
            return request.redirect('/')

        # Buscar primero si es una marca
        brand = request.env['brand.type'].sudo().search([
            '|', ('name', 'ilike', search), ('slug', '=', search.lower())
        ], limit=1)
        if brand:
            return request.redirect('/brand/' + (brand.slug or str(brand.id)))

        # Buscar si es una categoría
        category = request.env['product.category'].sudo().search([
            '|', ('name', 'ilike', search), ('slug', '=', search.lower())
        ], limit=1)
        if category:
            return request.redirect('/category/' + (category.slug or str(category.id)))

        # Si no es marca ni categoría, puedes redirigir a búsqueda general de productos
        return request.redirect('/shop?search=' + search)