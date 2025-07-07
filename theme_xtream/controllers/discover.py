from odoo import http
from odoo.http import request

class DiscoverController(http.Controller):

    @http.route('/discover', type='http', auth='public', website=True)
    def website_discover(self, **kw):
        # Usar el modelo de categorías internas (product.category)
        Category = request.env['product.category'].sudo()
        # Buscar todas las categorías y sus relaciones
        categories = Category.search([])
        # Contar cuántas veces cada categoría ha sido buscada (ajusta el campo según tu modelo)
        SearchLog = request.env['search.log'].sudo()
        category_counts = {}
        for cat in categories:
            count = SearchLog.search_count([('category_id', '=', cat.id)])
            category_counts[cat.id] = count

        # Construir la estructura jerárquica de categorías
        def build_category_tree(category):
            return {
            'id': category.id,
            'name': category.name,
            'count': category_counts.get(category.id, 0),
            'parent_id': category.parent_id.id if category.parent_id else None,
            'children': [build_category_tree(child) for child in category.child_id]
            }

        # Solo las categorías raíz
        root_categories = categories.filtered(lambda c: not c.parent_id)
        category_tree = [build_category_tree(cat) for cat in root_categories]

        return request.render('theme_xtream.website_discover', {
            'category_tree': category_tree,
        })
