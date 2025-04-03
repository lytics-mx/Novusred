from odoo import http
from odoo.http import request

class CustomShopController(http.Controller):

    @http.route(['/shop'], type='http', auth="public", website=True)
    def shop(self, category=None, brand=None, tag=None, offer=False, **kwargs):
        # Obtener categorías
        categories = request.env['product.public.category'].sudo().search([])

        # Obtener marcas
        brands = request.env['product.brand'].sudo().search([])

        # Obtener etiquetas
        tags = request.env['product.tag'].sudo().search([])

        # Filtrar productos en oferta
        domain = []
        if offer:
            domain.append(('is_discounted', '=', True))

        # Filtrar por categoría
        if category:
            domain.append(('public_categ_ids', 'in', int(category)))

        # Filtrar por marca
        if brand:
            domain.append(('brand_id', '=', int(brand)))

        # Filtrar por etiqueta
        if tag:
            domain.append(('tag_ids', 'in', int(tag)))

        # Obtener productos filtrados
        products = request.env['product.template'].sudo().search(domain)

        return request.render("theme_xtream.custom_products_sidebar", {
            'categories': categories,
            'brands': brands,
            'tags': tags,
            'products': products,
            'selected_category': int(category) if category else None,
            'selected_brand': int(brand) if brand else None,
            'selected_tag': int(tag) if tag else None,
        })