from odoo import http
from odoo.http import request

class BrandController(http.Controller):

    @http.route(['/brand'], type='http', auth="public", website=True)
    def shop_page(self, **kwargs):
        # Obtener todas las etiquetas disponibles (en lugar de marcas)
        tags = request.env['product.tags'].sudo().search([])

        # Obtener todas las categorías disponibles
        categories = request.env['product.public.category'].sudo().search([])

        # Filtrar productos según los parámetros (etiquetas y categorías)
        domain = []
        if 'tags' in kwargs:
            tag_ids = [int(t) for t in kwargs.getlist('tags')]
            domain.append(('product_tag_ids', 'in', tag_ids))
        if 'category' in kwargs:
            domain.append(('public_categ_ids', 'in', [int(kwargs['category'])]))

        # Obtener los productos filtrados
        products = request.env['product.template'].sudo().search(domain)

        # Determinar el tipo de vista (cuadrícula o lista)
        view_type = request.httprequest.cookies.get('view_type', 'grid')

        # Renderizar la plantilla con los datos
        return request.render('theme_xtream.product_grid_list_toggle', {
            'tags': tags,
            'categories': categories,
            'products': products,
            'view_type': view_type,
        })