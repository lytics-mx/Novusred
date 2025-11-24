from odoo import http
from odoo.http import request
import json
import re
import unicodedata

class WebsiteSearch(http.Controller):

    def _normalize(self, text):
        if not text:
            return ''
        text = unicodedata.normalize('NFKD', text)
        text = text.encode('ascii', 'ignore').decode('ascii')  # quita tildes
        return re.sub(r'\s+', ' ', text.strip().lower())

    def _sanitize_search(self, search):
        return (search or '').replace(' ', '-')

    @http.route('/search_redirect', auth='public', website=True)
    def search_redirect(self, search='', search_type='all', **kw):
        q = (search or '').strip()
        q_norm = self._normalize(q)
        Product = request.env['product.template'].sudo()
        Brand = request.env['brand.type'].sudo()
        Category = request.env['product.category'].sudo()

        if not q:
            return request.redirect('/subcategory')

        # Filtrado por tipo
        if search_type == 'brand':
            brand = Brand.search([('name', 'ilike', q)], limit=1)
            if brand:
                return request.redirect(f'/search_brand?brand_id={brand.id}')
            else:
                return request.redirect(f'/search_brand?search={self._sanitize_search(search)}')

        elif search_type == 'category':
            category = Category.search([('name', 'ilike', q)], limit=1)
            if category:
                return request.redirect(f'/search_category?category_id={category.id}')
            else:
                return request.redirect(f'/search_category?search={self._sanitize_search(search)}')

        elif search_type == 'product':
            product = Product.search([
                '|', ('name', 'ilike', q), ('product_model', 'ilike', q)
            ], limit=1)
            if product:
                return request.redirect(product.website_url or f'/shop/product/{product.id}')
            else:
                return request.redirect(f'/search_product?search={self._sanitize_search(search)}')

        # Si es "todos" o no se seleccionó filtro, sigue el flujo original
        # ...original logic for 'all'...
        # 1) Exact brand match (priority)
        brand = Brand.search([('name', 'ilike', q)], limit=1)
        if brand:
            return request.redirect(f'/subcategory?brand_id={brand.id}')

        # 2) Exact category match
        category = Category.search([('name', 'ilike', q)], limit=1)
        if category:
            return request.redirect(f'/subcategory?category_id={category.id}')

        # 3) Product by code (startswith)
        product = Product.search([('default_code', 'ilike', q + '%')], limit=1)
        if product:
            return request.redirect(product.website_url or f'/shop/product/{product.id}')

        # 4) Product by name or model
        product = Product.search(['|', ('name', 'ilike', q), ('product_model', 'ilike', q)], limit=1)
        if product:
            return request.redirect(product.website_url or f'/shop/product/{product.id}')

        # 5) Fallback fuzzy brand/category then general search page
        brand = Brand.search([('name', 'ilike', q)], limit=1)
        if brand:
            return request.redirect(f'/subcategory?brand_id={brand.id}')
        category = Category.search([('name', 'ilike', q)], limit=1)
        if category:
            return request.redirect(f'/subcategory?category_id={category.id}')

        search_sanitized = self._sanitize_search(search)
        return request.redirect(f'/subcategory?search={search_sanitized}')
# ...existing code...

    @http.route('/search_live', type='http', auth='public', website=True)
    def search_live(self, query=None, **kw):
        q = (query or '').strip()
        q_norm = self._normalize(q)
        Product = request.env['product.template'].sudo()
        Brand = request.env['brand.type'].sudo()
        Category = request.env['product.category'].sudo()

        results = []

        if not q:
            return request.make_response(json.dumps({'results': results}), headers=[('Content-Type', 'application/json')])

        # Brands (top)
        brands = Brand.search([('name', 'ilike', q)], limit=3)
        for b in brands:
            results.append({
                'id': b.id,
                'name': b.name,
                'type': 'brand',
                'url': f'/subcategory?brand_id={b.id}',
                'image': f'/web/image/brand.type/{b.id}/icon'
            })

        # Categories
        categories = Category.search([('name', 'ilike', q)], limit=3)
        for c in categories:
            results.append({
                'id': c.id,
                'name': c.name,
                'type': 'category',
                'url': f'/subcategory?category_id={c.id}',
                'image': f'/web/image/product.category/{c.id}/icon'
            })

        # Products by code (priority)
        products = Product.search([('default_code', 'ilike', q + '%')], order='list_price asc', limit=5)

        # If none by code, search by name/model (startswith/contains)
        if not products:
            products = Product.search([
                '|',
                ('name', 'ilike', q + '%'),
                ('product_model', 'ilike', q + '%')
            ], order='list_price asc', limit=8)

            # if still few results, broaden to contains
            if not products:
                products = Product.search([
                    '|',
                    ('name', 'ilike', q),
                    ('product_model', 'ilike', q)
                ], order='list_price asc', limit=8)

        for p in products:
            results.append({
                'id': p.id,
                'name': p.name,
                'type': 'product',
                'url': p.website_url or f'/shop/product/{p.id}',
                'image': f'/web/image/product.template/{p.id}/image_1024'
            })

        # Deduplicate by url (keep first occurrence)
        seen = set()
        dedup = []
        for r in results:
            if r['url'] in seen:
                continue
            seen.add(r['url'])
            dedup.append(r)

        return request.make_response(json.dumps({'results': dedup}), headers=[('Content-Type', 'application/json')])