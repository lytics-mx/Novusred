from odoo import http
from odoo.http import request
from datetime import datetime as Datetime
from pytz import timezone

class OffersController(http.Controller):

    @http.route('/offers', type='http', auth='public', website=True)
    def offers(self, **kwargs):
        # Filtros de la URL
        tag_id = kwargs.get('tag_id')
        brand_id = kwargs.get('brand_id')
        category_id = kwargs.get('category_id')
        free_shipping = kwargs.get('free_shipping', 'false').lower() == 'true'
        min_price = kwargs.get('min_price')
        max_price = kwargs.get('max_price')

        # Dominio base
        domain = [
            ('website_published', '=', True),
            ('sale_ok', '=', True),
            '|',
            ('discount_percentage', '>', 0),
            ('fixed_discount', '>', 0)
        ]
        if tag_id:
            try:
                domain.append(('product_tag_ids', 'in', int(tag_id)))
            except Exception:
                pass
        if brand_id:
            try:
                domain.append(('brand_id', '=', int(brand_id)))
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
                domain.append(('list_price', '>=', float(min_price)))
            except Exception:
                pass
        if max_price:
            try:
                domain.append(('list_price', '<=', float(max_price)))
            except Exception:
                pass

        # Buscar productos y calcular precio con descuento
        products = request.env['product.template'].sudo().search(domain)
        for product in products:
            if product.discount_percentage > 0:
                product.discounted_price = product.list_price * (1 - product.discount_percentage / 100)
            elif product.fixed_discount > 0:
                product.discounted_price = max(0, product.list_price - product.fixed_discount)
            else:
                product.discounted_price = product.list_price

        # Filtrar productos con descuento real
        discounted_products = products.filtered(lambda p: p.list_price > p.discounted_price)

        # Filtros de categorías principales
        all_categories = request.env['product.category'].sudo().search([])
        categories_with_count = []
        for cat in all_categories:
            cat_domain = list(domain) + [('categ_id', 'child_of', cat.id)]
            cat_products = request.env['product.template'].sudo().search(cat_domain)
            cat_products_with_discount = cat_products.filtered(lambda p: p.list_price > p.discounted_price)
            if cat_products_with_discount:
                categories_with_count.append({
                    'id': cat.id,
                    'name': cat.name,
                    'product_count': len(cat_products_with_discount),
                })

        # Filtros de marcas principales
        all_brands = request.env['brand.type'].sudo().search([])
        brands_with_count = []
        for brand in all_brands:
            brand_products_with_discount = brand.product_ids.filtered(lambda p: p in discounted_products)
            if brand_products_with_discount:
                brands_with_count.append({
                    'id': brand.id,
                    'name': brand.name,
                    'product_count': len(brand_products_with_discount),
                })
        # Filtros de etiquetas principales
        product_tags = request.env['product.tag'].sudo().search([
            ('visible_on_ecommerce', '=', True)
        ], limit=6)

        # Rangos de precio
        price_ranges = {
            '0_500': len([p for p in discounted_products if 0 < p.discounted_price <= 500]),
            '500_1000': len([p for p in discounted_products if 500 < p.discounted_price <= 1000]),
            '1000_plus': len([p for p in discounted_products if p.discounted_price > 1000]),
        }

        # Total de productos con descuento
        total_products = len(discounted_products)

        return request.render('theme_xtream.offers_template', {
            'discounted_products': discounted_products,
            'categories_with_count': categories_with_count,
            'brands_with_count': brands_with_count,
            'product_tags': product_tags,
            'price_ranges': price_ranges,
            'total_products': total_products,
            'selected_tag_id': tag_id,
            'selected_brand_id': brand_id,
            'selected_category_id': category_id,
            'free_shipping': free_shipping,
            'min_price': min_price,
            'max_price': max_price,
        })