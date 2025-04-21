from odoo import http
from odoo.http import request

class OffersController(http.Controller):

    @http.route('/shop/offers', type='http', auth='public', website=True)
    def offers_page(self, brand_id=None, category_id=None, **kwargs):
        # Filtrar productos publicados con descuento
        domain = [('website_published', '=', True), ('discount_price', '>', 0)]
        if brand_id:
            domain.append(('brand_id', '=', int(brand_id)))
        if category_id:
            domain.append(('categ_id', '=', int(category_id)))

        products = request.env['product.template'].sudo().search(domain)

        # Obtener marcas relacionadas con productos publicados
        brands = request.env['product.brand'].sudo().search([])
        for brand in brands:
            brand.product_count = request.env['product.template'].sudo().search_count(
                [('brand_id', '=', brand.id), ('website_published', '=', True)]
            )

        # Obtener categorías relacionadas con productos publicados
        categories = request.env['product.category'].sudo().search([])
        for category in categories:
            category.product_count = request.env['product.template'].sudo().search_count(
                [('categ_id', '=', category.id), ('website_published', '=', True)]
            )

        return request.render('theme_xtream.offers_template', {
            'discounted_products': products,
            'brands': brands,
            'categories': categories,
        })