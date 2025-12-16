from odoo import http
from odoo.http import request
import random

class DiscoverController(http.Controller):

    @http.route('/discover', type='http', auth='public', website=True)
    def website_discover(self, published_only=False, **kw):
        # Obtener todas las categorías
        categories = request.env['product.category'].sudo().search([])
        
        # Preparar datos con el contador de productos por categoría
        category_data = []
        for category in categories:
            domain = [('categ_id', 'child_of', category.id), ('qty_available', '>', 0)]
            if published_only:
                domain.append(('website_published', '=', True))  # Filtrar productos publicados
            
            product_count = request.env['product.template'].sudo().search_count(domain)
            if product_count > 0:  # Solo incluir categorías con al menos un producto
                category_data.append({
                    'name': category.name,
                    'product_count': product_count,
                    'category_id': category.id,  # Agregar category_id
                    'subcategory_id': category.parent_id.id if category.parent_id else category.id  # Agregar subcategory_id
                })
        
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