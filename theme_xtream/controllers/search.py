# No se indica filepath, colócalo en tu controlador de Odoo
from odoo import http
from odoo.http import request

class WebsiteSearch(http.Controller):

    @http.route('/search_redirect', auth='public', website=True)
    def search_redirect(self, search='', search_type='all', **kw):
        if search_type == 'brand':
            return request.redirect('/brand_search_redirect?search=%s' % search)
        elif search_type == 'category':
            return request.redirect('/category_search?search=%s' % search)
        else:
            # Redirige a /subcategory mostrando solo el producto buscado
            return request.redirect('/subcategory?search=%s' % search)