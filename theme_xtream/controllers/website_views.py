from odoo import http
from odoo.http import request

class WebsiteShop(http.Controller):

    @http.route('/shop', auth='public', website=True)
    def shop_products(self, brand=None, category=None, **kwargs):
        """
        Renderiza la página de productos con filtros opcionales por marca y categoría.
        """
        domain = [('website_published', '=', True)]  # Solo productos publicados en el sitio web

        # Filtrar por marca si se proporciona
        if brand:
            domain.append(('brand_type_id', '=', int(brand)))

        # Filtrar por categoría si se proporciona
        if category:
            domain.append(('public_categ_ids', 'child_of', int(category)))

        # Obtener los productos filtrados
        products = request.env['product.template'].sudo().search(domain, order='list_price desc')

        # Obtener todas las marcas disponibles
        brands = request.env['product.brand'].sudo().search([])

        # Obtener todas las categorías principales y sus subcategorías
        categories = request.env['product.public.category'].sudo().search([('parent_id', '=', False)])

        # Renderizar la plantilla con los productos filtrados, marcas y categorías
        return request.render('website_sale.products', {
            'products': products,
            'selected_brand': int(brand) if brand else None,
            'selected_category': int(category) if category else None,
            'brands': brands,
            'categories': categories,
        })