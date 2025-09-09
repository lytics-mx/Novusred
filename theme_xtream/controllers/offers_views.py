from odoo import http
from odoo.http import request

class OffersController(http.Controller):

    @http.route('/offers', type='http', auth='public', website=True)
    def offers(self, **kwargs):
        tag_id = kwargs.get('tag_id')
        brand_type_id = kwargs.get('brand_type_id')
        category_id = kwargs.get('category_id')
        free_shipping = kwargs.get('free_shipping', 'false').lower() == 'true'
        min_price = kwargs.get('min_price')
        max_price = kwargs.get('max_price')

        Product = request.env['product.template'].sudo()

        # Dominio base (incluye productos con "descuento" por los campos existentes)
        domain = [
            ('website_published', '=', True),
            ('sale_ok', '=', True),
            '|',
            ('discount_percentage', '>', 0),
            ('fixed_discount', '>', 0),
        ]
        if tag_id:
            try:
                domain.append(('product_tag_ids', 'in', [int(tag_id)]))
            except Exception:
                pass
        if brand_type_id:
            try:
                domain.append(('brand_type_id', '=', int(brand_type_id)))
            except Exception:
                pass
        if category_id:
            try:
                domain.append(('categ_id', 'child_of', int(category_id)))
            except Exception:
                pass
        if free_shipping:
            domain.append(('free_shipping', '=', True))

        # Elegir campo de precio para filtros: si existe discounted_price usarlo, si no usar list_price
        price_field = 'discounted_price' if 'discounted_price' in Product._fields else 'list_price'
        price_domain = []
        try:
            if min_price:
                min_price_val = float(min_price)
                price_domain.append((price_field, '>=', min_price_val))
        except Exception:
            min_price = None
        try:
            if max_price:
                max_price_val = float(max_price)
                price_domain.append((price_field, '<=', max_price_val))
        except Exception:
            max_price = None

        # Dominio para la lista final (base + filtros de precio si existen)
        page_domain = list(domain)
        page_domain.extend(price_domain)

        # Paginación: usar search_count + search con offset/limit
        current_page = max(1, int(kwargs.get('page', 1)))
        products_per_page = 15
        total_products = Product.search_count(page_domain)
        total_pages = max(1, (total_products + products_per_page - 1) // products_per_page)
        start = (current_page - 1) * products_per_page

        paged_products = Product.search(page_domain, offset=start, limit=products_per_page)

        # Price ranges: siempre sobre el dominio base (sin quitar filtros activos)
        price_ranges = {
            '0_500': Product.search_count(domain + [(price_field, '>', 0), (price_field, '<=', 500)]),
            '500_1000': Product.search_count(domain + [(price_field, '>', 500), (price_field, '<=', 1000)]),
            '1000_plus': Product.search_count(domain + [(price_field, '>', 1000)]),
        }

        # Conteos por marca (usar read_group, quitando solo el filtro de marca si estaba)
        domain_no_brand = [d for d in domain if not (isinstance(d, tuple) and d[0] == 'brand_type_id')]
        domain_no_brand.extend(price_domain)
        brand_groups = Product.read_group(domain_no_brand, ['brand_type_id'], ['brand_type_id'])
        brands_with_count = []
        for g in brand_groups:
            val = g.get('brand_type_id')
            if val:
                brands_with_count.append({
                    'id': val[0],
                    'name': val[1],
                    'product_count': g.get('brand_type_id_count', 0),
                })

        # Conteos por categoría (read_group sobre categ_id)
        domain_no_category = [d for d in domain if not (isinstance(d, tuple) and d[0] == 'categ_id')]
        domain_no_category.extend(price_domain)
        cat_groups = Product.read_group(domain_no_category, ['categ_id'], ['categ_id'])
        categories_with_count = []
        for g in cat_groups:
            val = g.get('categ_id')
            if val:
                categories_with_count.append({
                    'id': val[0],
                    'name': val[1],
                    'product_count': g.get('categ_id_count', 0),
                })

        # Tags con descuento (read_group por product_tag_ids), filtrar por visibilidad si se desea
        domain_no_tag = [d for d in domain if not (isinstance(d, tuple) and d[0] == 'product_tag_ids')]
        domain_no_tag.extend(price_domain)
        tag_groups = Product.read_group(domain_no_tag, ['product_tag_ids'], ['product_tag_ids'])
        tags_with_discount = []
        # Obtener solo tags visibles/activas para mostrar
        visible_tag_ids = set(t.id for t in request.env['product.tag'].sudo().search([
            ('is_active', '=', True), ('visible_on_ecommerce', '=', True)
        ]))
        for g in tag_groups:
            val = g.get('product_tag_ids')
            if val and val[0] in visible_tag_ids:
                tag_rec = request.env['product.tag'].sudo().browse(val[0])
                tags_with_discount.append(tag_rec)

        # Obtener listas auxiliares (tags, all_offer_tags, all categories pequeñas queries)
        product_tags = request.env['product.tag'].sudo().search([
            ('is_active', '=', True),
            ('visible_on_ecommerce', '=', True)
        ])
        all_offer_tags = request.env['product.tag'].sudo().search([
            ('is_active', '=', True),
            ('visible_on_ecommerce', '=', True)
        ])
        main_categories = request.env['product.category'].sudo().browse([c['categ_id'][0] for c in cat_groups if c.get('categ_id')])

        current_filters = {
            'tag_id': tag_id,
            'brand_type_id': brand_type_id,
            'category_id': category_id,
            'free_shipping': 'true' if free_shipping else '',
            'min_price': min_price,
            'max_price': max_price,
        }
        current_filters = {k: v for k, v in current_filters.items() if v}

        return request.render('theme_xtream.offers_template', {
            'discounted_products': paged_products,
            'current_page': current_page,
            'total_pages': total_pages,
            'current_filters': current_filters,

            'categories_with_count': categories_with_count,
            'total_products': total_products,
            'price_ranges': price_ranges,
            'all_categories': main_categories,
            'free_shipping': free_shipping,
            'tags_with_discount': tags_with_discount,
            'selected_tag_id': tag_id,
            'selected_brand_type_id': brand_type_id,
            'selected_category_id': category_id,
            'brands_with_count': brands_with_count,
            'min_price': min_price,
            'max_price': max_price,
            'product_tags': product_tags,
            'all_offer_tags': all_offer_tags,
        })
