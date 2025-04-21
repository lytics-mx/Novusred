from odoo import http
from odoo.http import request

class OffersController(http.Controller):

    @http.route('/offers', type='http', auth='public', website=True)
    def offers(self, **kwargs):
        """Renderiza la página de productos en oferta."""
        # Filtrar productos publicados que tengan al menos una etiqueta
        tagged_products = request.env['product.template'].sudo().search([
            ('website_published', '=', True),
            ('product_tag_ids', '!=', False)  # Productos relacionados con etiquetas
        ])

        # Obtener todas las marcas relacionadas con productos
        brands = request.env['brand.type'].sudo().search([])
        for brand in brands:
            # Contar productos relacionados con cada marca
            brand.product_count = request.env['product.template'].sudo().search_count([
                ('brand_type_id', '=', brand.id),
                ('website_published', '=', True)
            ])

        return request.render('theme_xtream.offers_template', {
            'discounted_products': tagged_products,
            'brands': brands
        })