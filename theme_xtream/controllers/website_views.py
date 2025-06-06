from odoo import http
from odoo.http import request
from datetime import datetime as Datetime
from pytz import timezone

class OffersController(http.Controller):

    @http.route('/offers', type='http', auth='public', website=True)
    def offers(self, **kwargs):
        # --- 1. Obtener parámetros de filtro ---
        tag_id = kwargs.get('tag_id')
        brand_type_id = kwargs.get('brand_type_id')
        free_shipping = kwargs.get('free_shipping', 'false').lower() == 'true'
        min_price = kwargs.get('min_price')
        max_price = kwargs.get('max_price')

        # --- 2. Construir dominio base ---
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

        # --- 3. Buscar productos filtrados y con descuento real ---
        Product = request.env['product.template'].sudo()
        products = Product.search(domain)
        discounted_products = products.filtered(lambda p: p.list_price > p.discounted_price)

        # --- 4. Calcular price_ranges ---
        price_ranges = {
            '0_500': len(discounted_products.filtered(lambda p: 0 < p.discounted_price <= 500)),
            '500_1000': len(discounted_products.filtered(lambda p: 500 < p.discounted_price <= 1000)),
            '1000_plus': len(discounted_products.filtered(lambda p: p.discounted_price > 1000)),
        }

        # --- 5. Obtener marcas y categorías con conteo ---
        BrandType = request.env['brand.type'].sudo()
        all_brand_types = BrandType.search([])
        brands_with_count = []
        for brand in all_brand_types:
            brand_domain = domain.copy()
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

        all_categories = request.env['product.category'].sudo().search([])
        main_categories = [
            cat for cat in all_categories
            if Product.search_count(domain + [('categ_id', 'child_of', cat.id)]) > 0
        ]
        categories_with_count = []
        for cat in main_categories:
            cat_domain = domain.copy()
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

        # --- 6. Obtener tags con descuento ---
        ProductTag = request.env['product.tag'].sudo()
        tags_with_discount = []
        for tag in ProductTag.search([('visible_on_ecommerce', '=', True)]):
            prods = Product.search(domain + [('product_tag_ids', 'in', tag.id)])
            prods_with_discount = prods.filtered(lambda p: p.list_price > p.discounted_price)
            if prods_with_discount:
                tags_with_discount.append(tag)

        # --- 7. Renderizar plantilla ---
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
            'brands_with_count': brands_with_count,
        })