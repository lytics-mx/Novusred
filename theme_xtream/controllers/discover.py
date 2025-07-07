from odoo import http
from odoo.http import request
import random

class DiscoverController(http.Controller):

    @http.route('/discover', type='http', auth='public', website=True)
    def website_discover(self, **kw):
        # Obtener todas las categorías
        categories = request.env['product.category'].sudo().search([])
        
        # Preparar datos con el contador de productos por categoría
        category_data = []
        for category in categories:
            product_count = request.env['product.template'].sudo().search_count([
                ('categ_id', 'child_of', category.id),
                ('qty_available', '>', 1)  # Filtrar productos con stock mayor a 1
            ])
            if product_count > 0:  # Solo incluir categorías con al menos un producto
                category_data.append({
                    'name': category.name,
                    'product_count': product_count
                })
        
        # Mezclar las categorías aleatoriamente
        random.shuffle(category_data)
        
        # Dividir las categorías en tres columnas con un límite de 6 nombres por columna
        columns = [category_data[i * 6:(i + 1) * 6] for i in range(3)]
        
        # Eliminar columnas vacías
        columns = [column for column in columns if column]

        # Renderizar el template con los datos
        return request.render('theme_xtream.website_discover', {
            'columns': columns
        })