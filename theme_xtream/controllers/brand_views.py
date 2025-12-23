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
        try:
            current_page = int(request.params.get('page', 1))
        except Exception:
            current_page = 1
        per_page = 20
        total_products = request.env['product.template'].sudo().search_count(domain)
        total_pages = max(1, (total_products + per_page - 1) // per_page)
        start = (current_page - 1) * per_page
        products = request.env['product.template'].sudo().search(domain, offset=start, limit=per_page)

        # Si no hay productos publicados, redirige a /brand
        if not products:
            return request.redirect('/brand')



        # Categorías principales de los productos paginados
        category_ids = products.mapped('categ_id').ids
        categories = request.env['product.category'].sudo().browse(category_ids)

        # Optimizar subcategorías: solo buscar hijos con productos publicados de la marca en lote
        valid_categories = []
        if categories:
            # Buscar todos los hijos de todas las categorías de una vez
            all_child_ids = sum([cat.child_id.ids for cat in categories], [])
            if all_child_ids:
                # Buscar cuántos productos publicados hay por subcategoría-hijo en lote
                subcat_counts = request.env['product.template'].sudo().read_group(
                    [
                        ('categ_id', 'in', all_child_ids),
                        ('brand_type_id', '=', brand_type_rec.id),
                        ('website_published', '=', True)
                    ],
                    ['categ_id'], ['categ_id']
                )
                subcat_id_with_products = set(row['categ_id'][0] for row in subcat_counts if row['categ_id'])
            else:
                subcat_id_with_products = set()
            for cat in categories:
                valid_children = [c for c in cat.child_id if c.id in subcat_id_with_products]
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
    
