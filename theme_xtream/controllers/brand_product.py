from odoo import http
from odoo.http import request

class BrandController(http.Controller):

    @http.route(['/brand'], type='http', auth="public", website=True)
    def shop_page(self, **kwargs):
        # Obtener todas las marcas disponibles
        brands = request.env['product.brand'].sudo().search([])

        # Obtener todas las categorías disponibles
        categories = request.env['product.public.category'].sudo().search([])

        # Obtener todas las etiquetas disponibles
        tags = request.env['product.tags'].sudo().search([])

        # Filtrar productos según los parámetros (marca, categoría y etiquetas)
        domain = []
        if 'brand_filter' in kwargs:
            brand_ids = [int(b) for b in kwargs.getlist('brand_filter')]
            domain.append(('product_brand_id', 'in', brand_ids))
        if 'category' in kwargs:
            domain.append(('public_categ_ids', 'in', [int(kwargs['category'])]))
        if 'tags' in kwargs:
            tag_ids = [int(t) for t in kwargs.getlist('tags')]
            domain.append(('product_tag_ids', 'in', tag_ids))

        # Obtener los productos filtrados
        products = request.env['product.template'].sudo().search(domain)

        # Determinar el tipo de vista (cuadrícula o lista)
        view_type = request.httprequest.cookies.get('view_type', 'grid')

        # Renderizar la plantilla con los datos
        return request.render('theme_xtream.product_grid_list_toggle', {
            'brands': brands,
            'categories': categories,
            'tags': tags,
            'products': products,
            'view_type': view_type,
        })