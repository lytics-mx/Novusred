from odoo import http
from odoo.http import request
import random

class DiscoverController(http.Controller):

    @http.route('/discover', type='http', auth='public', website=True)
    def website_discover(self, published_only=False, **kw):
        # Obtener todas las categorías
        categories = request.env['product.category'].sudo().search([])

        # Función recursiva para obtener todos los niveles de categorías
        def get_category_hierarchy(category):
            hierarchy = {
                'name': category.name,
                'category_id': category.id,
                'product_count': 0,  # Inicializar el contador de productos
                'children': []
            }
            # Obtener subcategorías
            subcategories = request.env['product.category'].sudo().search([('parent_id', '=', category.id)])
            for subcategory in subcategories:
                hierarchy['children'].append(get_category_hierarchy(subcategory))
            return hierarchy

        # Preparar datos con el contador de productos por categoría
        category_data = []
        for category in categories.filtered(lambda c: not c.parent_id):  # Solo categorías principales
            hierarchy = get_category_hierarchy(category)
            domain = [('categ_id', 'child_of', category.id), ('qty_available', '>', 0)]
            if published_only:
                domain.append(('website_published', '=', True))  # Filtrar productos publicados
            
            product_count = request.env['product.template'].sudo().search_count(domain)
            if product_count > 0:  # Solo incluir categorías con al menos un producto
                hierarchy['product_count'] = product_count
                category_data.append(hierarchy)

        # Mezclar las categorías aleatoriamente
        random.shuffle(category_data)

        # Dividir las categorías en tres columnas con un límite de 6 nombres por columna
        columns = [category_data[i * 6:(i + 1) * 6] for i in range(3)]

        # Eliminar columnas vacías
        columns = [column for column in columns if column]

        # Renderizar el template con los datos
        return request.render('theme_xtream.website_discover', {
            'categories': category_data,
            'columns': columns
        })