from odoo import http
from odoo.http import request

class WebsiteSearch(http.Controller):

    @http.route('/search_redirect', auth='public', website=True)
    def search_redirect(self, search='', search_type='all'):
        # Limpiar el texto de búsqueda
        search = search.strip()
        
        if not search:
            return request.redirect('/subcategory')
        
        # 1. BÚSQUEDA AUTOMÁTICA POR CÓDIGO DE PRODUCTO (default_code)
        # Primero verificar si el texto de búsqueda es un código de producto
        Product = request.env['product.template'].sudo()
        product_by_code = Product.search([('default_code', '=ilike', search)], limit=1)
        
        if product_by_code:
            # Si encuentra el producto por código, redirigir directamente
            return request.redirect('/shop/%s?product=product.template(%s,)' % (product_by_code.slug(), product_by_code.id))
        
        # 2. BÚSQUEDA POR FILTRO ESPECÍFICO
        if search_type == 'brand':
            return request.redirect('/brand_search_redirect?search=%s' % search)
        elif search_type == 'category':
            return request.redirect('/category_search?search=%s' % search)
        elif search_type == 'model':
            # Buscar producto por modelo (Referencia)
            product = Product.search([('default_code', '=', search)], limit=1)
            if product:
                return request.redirect('/shop/%s?product=product.template(%s,)' % (product.slug(), product.id))
            else:
                return request.redirect('/subcategory?search=%s' % search)
        else:
            # 3. BÚSQUEDA INTELIGENTE AUTOMÁTICA (search_type='all')
            
            # Buscar por marca primero
            Brand = request.env['brand.type.id'].sudo()
            brand = Brand.search([('name', '=ilike', search)], limit=1)
            
            if brand:
                # Si encuentra una marca, redirigir a subcategory con el brand_id
                return request.redirect('/subcategory?brand_id=%s' % brand.id)
            
            # Buscar marcas que contengan el texto (búsqueda parcial)
            brands_partial = Brand.search([('name', 'ilike', search)], limit=5)
            if brands_partial:
                # Si encuentra marcas parciales, usar la primera
                return request.redirect('/subcategory?brand_id=%s' % brands_partial[0].id)
            
            # Buscar por categoría
            Category = request.env['product.category'].sudo()
            category = Category.search([('name', '=ilike', search)], limit=1)
            
            if category:
                # Si encuentra una categoría, redirigir con category_id
                return request.redirect('/subcategory?category_id=%s' % category.id)
            
            # Buscar categorías que contengan el texto (búsqueda parcial)
            categories_partial = Category.search([('name', 'ilike', search)], limit=5)
            if categories_partial:
                # Si encuentra categorías parciales, usar la primera
                return request.redirect('/subcategory?category_id=%s' % categories_partial[0].id)
            
            # Buscar productos por nombre
            products_by_name = Product.search([('name', 'ilike', search)], limit=5)
            if products_by_name:
                # Si encuentra productos, buscar la marca más común entre ellos
                brand_ids = products_by_name.mapped('product_brand_id')
                if brand_ids:
                    # Usar la marca del primer producto encontrado
                    return request.redirect('/subcategory?brand_id=%s&search=%s' % (brand_ids[0].id, search))
            
            # Si no encuentra nada específico, búsqueda general en subcategory
            return request.redirect('/subcategory?search=%s' % search)