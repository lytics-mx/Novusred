from odoo import http

class CategoryController(http.Controller):
    
    @http.route('/category', auth='public', website=True)
    def category(self, **kw):
        """
        Renderiza la página de categoría con contenido dinámico.
        """
        return http.request.render('theme_xtream.website_category')  