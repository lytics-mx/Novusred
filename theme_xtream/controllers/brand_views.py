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



        # Implementar paginación real para productos
        # Paginación rápida y solo traer campos esenciales
        try:
            current_page = int(request.params.get('page', 1))
        except Exception:
            current_page = 1
        per_page = 10
        total_products = request.env['product.template'].sudo().search_count(domain)
        total_pages = max(1, (total_products + per_page - 1) // per_page)
        start = (current_page - 1) * per_page
        products = request.env['product.template'].sudo().search(domain, offset=start, limit=per_page, fields=['id','name'])

        # Si no hay productos publicados, redirige a /brand
        if not products:
            return request.redirect('/brand')



        # Categorías principales de los productos paginados
        # Solo obtener los IDs de categoría de los productos paginados
        # No buscar categorías ni hijos para máxima velocidad
        valid_categories = []

        # Obtener la imagen de banner del campo banner_image de la primera categoría (si existe)
        banner_image = False


        return request.render('theme_xtream.brand_search', {
            'brand_type': brand_type_rec,
            'products': products,
            'categories': valid_categories,  # Ahora es una lista de dicts
            'banner_image': banner_image,
            'current_page': current_page,
            'total_pages': total_pages,
            'total_products': total_products,
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
    
