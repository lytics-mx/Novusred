from odoo import http
from odoo.http import request

class WebsiteBrand(http.Controller):

    @http.route('/brand/<string:brand_name>', auth='public', website=True)
    def brand_products(self, brand_name, subcat_id=None, **kwargs):
        BrandType = request.env['brand.type']
        brand_type_rec = BrandType.sudo().search([
            ('slug', '=', brand_name.lower()),
            ('active', '=', True)
        ], limit=1)
        if not brand_type_rec:
            return request.not_found()

        domain = [
            ('brand_type_id', '=', brand_type_rec.id),
            ('website_published', '=', True)
        ]
        # Si hay subcat_id, filtra por esa subcategoría
        subcat_id = request.params.get('subcat_id')
        if subcat_id:
            domain.append(('categ_id', '=', int(subcat_id)))

        products = request.env['product.template'].sudo().search(domain)

        # Categorías y subcategorías para el template
        category_ids = products.mapped('categ_id').ids
        categories = request.env['product.category'].sudo().browse(category_ids)

        # Obtener la imagen de banner del campo banner_image
        # ...existing code...
        
        # Obtener la imagen de banner del campo banner_image de la primera categoría (si existe)
        banner_image = categories[0].banner_image if categories and hasattr(categories[0], 'banner_image') else False
        
        # ...existing code...
        return request.render('theme_xtream.brand_search', {
            'brand_type': brand_type_rec,
            'products': products,
            'categories': categories,
            'banner_image': banner_image,
        })

    @http.route('/brand_search_redirect', type='http', auth='public', website=True)
    def brand_search_redirect(self, search=None, **kwargs):
        if search:
            BrandType = request.env['brand.type'].sudo()
            # Primero busca coincidencia exacta (insensible a mayúsculas)
            brand = BrandType.search([('name', '=', search)], limit=1)
            if not brand:
                # Si no hay coincidencia exacta, busca parcial
                brand = BrandType.search([('name', 'ilike', search)], limit=1)
            if brand:
                brand_name_url = brand.slug
                return request.redirect('/brand/%s' % brand_name_url)
        return request.redirect('/brand')

    @http.route('/brand', auth='public', website=True)
    def home(self):
        products = request.env['product.template'].sudo().search([('website_published', '=', True)], order='create_date desc', limit=10)
        return http.request.render('theme_xtream.website_brand', {
            'products': products,
        })
    
