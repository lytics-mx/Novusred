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


        # Limitar la cantidad de productos traídos para evitar time-out
        products = request.env['product.template'].sudo().search(domain, limit=60)

        # Si no hay productos publicados, redirige a /brand
        if not products:
            return request.redirect('/brand')


        # Categorías principales de los productos (limitando para evitar traer demasiadas)
        category_ids = products.mapped('categ_id').ids[:30]
        categories = request.env['product.category'].sudo().browse(category_ids)

        # Filtrar solo subcategorías (child) que tengan productos publicados de la marca, limitando la búsqueda
        valid_categories = []
        for cat in categories:
            # Limitar a máximo 20 hijos por categoría
            children = cat.child_id[:20]
            valid_children = []
            for c in children:
                count = request.env['product.template'].sudo().search_count([
                    ('categ_id', '=', c.id),
                    ('brand_type_id', '=', brand_type_rec.id),
                    ('website_published', '=', True)
                ])
                if count > 0:
                    valid_children.append(c)
            if valid_children:
                valid_categories.append({
                    'cat': cat,
                    'valid_children': valid_children,
                })

        # Obtener la imagen de banner del campo banner_image de la primera categoría (si existe)
        banner_image = valid_categories[0]['cat'].banner_image if valid_categories and hasattr(valid_categories[0]['cat'], 'banner_image') else False

        return request.render('theme_xtream.brand_search', {
            'brand_type': brand_type_rec,
            'products': products,
            'categories': valid_categories,  # Ahora es una lista de dicts
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
    
