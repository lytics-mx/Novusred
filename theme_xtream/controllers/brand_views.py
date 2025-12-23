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

        products = request.env['product.template'].sudo().search(domain, limit=60)
        if not products:
            return request.redirect('/brand')

        # Obtener todas las categorías y subcategorías con productos publicados de la marca en lote
        categ_ids = products.mapped('categ_id').ids
        # Buscar hijos en lote usando read_group para máxima velocidad
        subcat_counts = request.env['product.template'].sudo().read_group([
            ('brand_type_id', '=', brand_type_rec.id),
            ('website_published', '=', True)
        ], ['categ_id'], ['categ_id'])
        subcat_ids = set(row['categ_id'][0] for row in subcat_counts if row['categ_id'])
        categories = request.env['product.category'].sudo().browse(categ_ids)
        valid_categories = []
        for cat in categories:
            valid_children = [c for c in cat.child_id if c.id in subcat_ids]
            valid_categories.append({
                'cat': cat,
                'valid_children': valid_children,
            })
        banner_image = valid_categories[0]['cat'].banner_image if valid_categories and hasattr(valid_categories[0]['cat'], 'banner_image') else False
        return request.render('theme_xtream.brand_search', {
            'brand_type': brand_type_rec,
            'products': products,
            'categories': valid_categories,
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
    
