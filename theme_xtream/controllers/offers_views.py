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

        # Dominio base con todos los filtros activos (excepto precio)
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

        Product = request.env['product.template'].sudo()
        products = Product.search(domain)
        discounted_products = products.filtered(lambda p: p.list_price > (p.discounted_price if hasattr(p, 'discounted_price') else p.list_price))
        product_tags = request.env['product.tag'].sudo().search([
            ('is_active', '=', True),
            ('visible_on_ecommerce', '=', True)
        ])
        all_offer_tags = request.env['product.tag'].search([
            ('is_active', '=', True),
            ('visible_on_ecommerce', '=', True)
        ])        
        # Filtro de precio en Python (sobre discounted_products)
        if min_price:
            try:
                min_price_val = float(min_price)
                discounted_products = discounted_products.filtered(
                    lambda p: (p.discounted_price if hasattr(p, 'discounted_price') else p.list_price) >= min_price_val
                )
            except Exception:
                pass
        if max_price:
            try:
                max_price_val = float(max_price)
                discounted_products = discounted_products.filtered(
                    lambda p: (p.discounted_price if hasattr(p, 'discounted_price') else p.list_price) <= max_price_val
                )
            except Exception:
                pass

        # Price ranges: SIEMPRE usar el dominio base (sin quitar ningún filtro)
        price_ranges = {
            '0_500': len(products.filtered(lambda p: 0 < (p.discounted_price if hasattr(p, 'discounted_price') else p.list_price) <= 500 and p.list_price > (p.discounted_price if hasattr(p, 'discounted_price') else p.list_price))),
            '500_1000': len(products.filtered(lambda p: 500 < (p.discounted_price if hasattr(p, 'discounted_price') else p.list_price) <= 1000 and p.list_price > (p.discounted_price if hasattr(p, 'discounted_price') else p.list_price))),
            '1000_plus': len(products.filtered(lambda p: (p.discounted_price if hasattr(p, 'discounted_price') else p.list_price) > 1000 and p.list_price > (p.discounted_price if hasattr(p, 'discounted_price') else p.list_price))),
        }

        # Marcas con conteo (quita solo el filtro de marca, aplica los demás y el filtro de precio si está activo)
        BrandType = request.env['brand.type'].sudo()
        all_brand_types = BrandType.search([])
        brands_with_count = []
        for brand in all_brand_types:
            brand_domain = [d for d in domain if not (isinstance(d, tuple) and d[0] == 'brand_type_id')]
            brand_domain.append(('brand_type_id', '=', brand.id))
            brand_products = Product.search(brand_domain)
            brand_products_with_discount = brand_products.filtered(lambda p: p.list_price > (p.discounted_price if hasattr(p, 'discounted_price') else p.list_price))
            # Aplica el filtro de precio si está activo
            if min_price:
                try:
                    min_price_val = float(min_price)
                    brand_products_with_discount = brand_products_with_discount.filtered(
                        lambda p: (p.discounted_price if hasattr(p, 'discounted_price') else p.list_price) >= min_price_val
                    )
                except Exception:
                    pass
            if max_price:
                try:
                    max_price_val = float(max_price)
                    brand_products_with_discount = brand_products_with_discount.filtered(
                        lambda p: (p.discounted_price if hasattr(p, 'discounted_price') else p.list_price) <= max_price_val
                    )
                except Exception:
                    pass
            prod_count = len(brand_products_with_discount)
            if prod_count > 0:
                brands_with_count.append({
                    'id': brand.id,
                    'name': brand.name,
                    'product_count': prod_count,
                })

        # Categorías con conteo (quita solo el filtro de categoría, aplica los demás y el filtro de precio si está activo)
        all_categories = request.env['product.category'].sudo().search([])
        main_categories = [
            cat for cat in all_categories
            if Product.search_count(domain + [('categ_id', 'child_of', cat.id)]) > 0
        ]
        categories_with_count = []
        for cat in main_categories:
            cat_domain = [d for d in domain if not (isinstance(d, tuple) and d[0] == 'categ_id')]
            cat_domain.append(('categ_id', 'child_of', cat.id))
            cat_products = Product.search(cat_domain)
            cat_products_with_discount = cat_products.filtered(lambda p: p.list_price > (p.discounted_price if hasattr(p, 'discounted_price') else p.list_price))
            # Aplica el filtro de precio si está activo
            if min_price:
                try:
                    min_price_val = float(min_price)
                    cat_products_with_discount = cat_products_with_discount.filtered(
                        lambda p: (p.discounted_price if hasattr(p, 'discounted_price') else p.list_price) >= min_price_val
                    )
                except Exception:
                    pass
            if max_price:
                try:
                    max_price_val = float(max_price)
                    cat_products_with_discount = cat_products_with_discount.filtered(
                        lambda p: (p.discounted_price if hasattr(p, 'discounted_price') else p.list_price) <= max_price_val
                    )
                except Exception:
                    pass
            prod_count = len(cat_products_with_discount)
            if prod_count > 0:
                categories_with_count.append({
                    'id': cat.id,
                    'name': cat.name,
                    'product_count': prod_count,
                })

        # Tags con descuento (quita solo el filtro de tag, aplica los demás y el filtro de precio si está activo)
        ProductTag = request.env['product.tag'].sudo()
        tags_with_discount = []
        for tag in ProductTag.search([('visible_on_ecommerce', '=', True)]):
            tag_domain = [d for d in domain if not (isinstance(d, tuple) and d[0] == 'product_tag_ids')]
            tag_domain.append(('product_tag_ids', 'in', [tag.id]))
            prods = Product.search(tag_domain)
            prods_with_discount = prods.filtered(lambda p: p.list_price > (p.discounted_price if hasattr(p, 'discounted_price') else p.list_price))
            # Aplica el filtro de precio si está activo
            if min_price:
                try:
                    min_price_val = float(min_price)
                    prods_with_discount = prods_with_discount.filtered(
                        lambda p: (p.discounted_price if hasattr(p, 'discounted_price') else p.list_price) >= min_price_val
                    )
                except Exception:
                    pass
            if max_price:
                try:
                    max_price_val = float(max_price)
                    prods_with_discount = prods_with_discount.filtered(
                        lambda p: (p.discounted_price if hasattr(p, 'discounted_price') else p.list_price) <= max_price_val
                    )
                except Exception:
                    pass
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
            'product_tags': product_tags,
            'all_offer_tags': all_offer_tags,
        })