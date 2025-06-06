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

        # 1. Dominio base con todos los filtros activos
        domain = [
            ('website_published', '=', True),
            ('sale_ok', '=', True),
            '|',
            ('discount_percentage', '>', 0),
            ('fixed_discount', '>', 0)
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
        if min_price:
            try:
                domain.append(('discounted_price', '>=', float(min_price)))
            except Exception:
                pass
        if max_price:
            try:
                domain.append(('discounted_price', '<=', float(max_price)))
            except Exception:
                pass

        Product = request.env['product.template'].sudo()
        products = Product.search(domain)
        discounted_products = products.filtered(lambda p: p.list_price > p.discounted_price)

        # 2. Price ranges (usando el mismo dominio)
        price_ranges = {
            '0_500': len(discounted_products.filtered(lambda p: 0 < p.discounted_price <= 500)),
            '500_1000': len(discounted_products.filtered(lambda p: 500 < p.discounted_price <= 1000)),
            '1000_plus': len(discounted_products.filtered(lambda p: p.discounted_price > 1000)),
        }

        # 3. Marcas con conteo (usando el mismo dominio base + filtro de marca)
        BrandType = request.env['brand.type'].sudo()
        all_brand_types = BrandType.search([])
        brands_with_count = []
        for brand in all_brand_types:
            brand_domain = domain.copy()
            # Quita el filtro de marca actual si existe, para que el conteo sea correcto
            brand_domain = [d for d in brand_domain if not (isinstance(d, tuple) and d[0] == 'brand_type_id')]
            brand_domain.append(('brand_type_id', '=', brand.id))
            brand_products = Product.search(brand_domain)
            brand_products_with_discount = brand_products.filtered(lambda p: p.list_price > p.discounted_price)
            prod_count = len(brand_products_with_discount)
            if prod_count > 0:
                brands_with_count.append({
                    'id': brand.id,
                    'name': brand.name,
                    'product_count': prod_count,
                })

        # 4. Categorías con conteo (usando el mismo dominio base + filtro de categoría)
        all_categories = request.env['product.category'].sudo().search([])
        main_categories = [
            cat for cat in all_categories
            if Product.search_count(domain + [('categ_id', 'child_of', cat.id)]) > 0
        ]
        categories_with_count = []
        for cat in main_categories:
            cat_domain = domain.copy()
            # Quita el filtro de categoría actual si existe, para que el conteo sea correcto
            cat_domain = [d for d in cat_domain if not (isinstance(d, tuple) and d[0] == 'categ_id')]
            cat_domain.append(('categ_id', 'child_of', cat.id))
            cat_products = Product.search(cat_domain)
            cat_products_with_discount = cat_products.filtered(lambda p: p.list_price > p.discounted_price)
            prod_count = len(cat_products_with_discount)
            if prod_count > 0:
                categories_with_count.append({
                    'id': cat.id,
                    'name': cat.name,
                    'product_count': prod_count,
                })

        # 5. Tags con descuento (usando el mismo dominio base + filtro de tag)
        ProductTag = request.env['product.tag'].sudo()
        tags_with_discount = []
        for tag in ProductTag.search([('visible_on_ecommerce', '=', True)]):
            tag_domain = domain.copy()
            tag_domain = [d for d in tag_domain if not (isinstance(d, tuple) and d[0] == 'product_tag_ids')]
            tag_domain.append(('product_tag_ids', 'in', tag.id))
            prods = Product.search(tag_domain)
            prods_with_discount = prods.filtered(lambda p: p.list_price > p.discounted_price)
            if prods_with_discount:
                tags_with_discount.append(tag)

        return request.render('theme_xtream.offers_template', {
            'discounted_products': discounted_products,
            'categories_with_count': categories_with_count,
            'total_products': len(discounted_products),
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
        })