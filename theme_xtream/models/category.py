from odoo import http
from odoo.http import request

class CategoryController(http.Controller):

    @http.route('/category', auth='public', website=True)
    def home(self):
        return http.request.render('theme_xtream.website_category')  

    @http.route('/subcategory', auth='public', website=True)
    def category(self, category_id=None, subcategory_id=None, brand_id=None, 
                 free_shipping=None, min_price=None, max_price=None, price_range=None,
                 discount_id=None, promotion_id=None, sort=None, **kw):
        """
        Renderiza la página de subcategoría con filtros dinámicos.
        SOLO productos publicados aparecerán en marcas, categorías, ofertas y rangos de precio.
        """
        # Obtener todas las categorías principales QUE TENGAN PRODUCTOS PUBLICADOS
        published_products_categories = request.env['product.template'].sudo().search([
            ('website_published', '=', True)
        ]).mapped('categ_id')
        
        categories = request.env['product.category'].sudo().search([
            ('parent_id', '=', False),
            ('id', 'in', published_products_categories.ids)
        ])
        
        # Construir dominio base SOLO para productos publicados
        domain = [('website_published', '=', True)]
        
        # Variables para la vista
        selected_category = None
        selected_subcategory = None
        selected_brand = None
        subcategories = []
        
        # Filtro por categoría (ESTE ES EL PRINCIPAL)
        if category_id:
            try:
                category_id = int(category_id)
                domain.append(('categ_id', 'child_of', category_id))
                selected_category = request.env['product.category'].sudo().browse(category_id)
                
                # Buscar subcategorías QUE TENGAN PRODUCTOS PUBLICADOS
                category_published_products = request.env['product.template'].sudo().search([
                    ('website_published', '=', True),
                    ('categ_id', 'child_of', category_id)
                ])
                subcategory_ids = category_published_products.mapped('categ_id').filtered(
                    lambda c: c.parent_id.id == category_id
                )
                subcategories = subcategory_ids
            except (ValueError, TypeError):
                category_id = None
        
        # Filtro por subcategoría
        if subcategory_id:
            try:
                subcategory_id = int(subcategory_id)
                # Si hay subcategoría, filtrar exactamente por ella (no child_of)
                domain = [d for d in domain if d[0] != 'categ_id']  # Remover filtro de categoría padre
                domain.append(('categ_id', '=', subcategory_id))
                selected_subcategory = request.env['product.category'].sudo().browse(subcategory_id)
            except (ValueError, TypeError):
                subcategory_id = None
        
        # Filtro por marca
        if brand_id:
            try:
                brand_id = int(brand_id)
                domain.append(('brand_type_id', '=', brand_id))
                selected_brand = request.env['brand.type'].sudo().browse(brand_id)
            except (ValueError, TypeError):
                brand_id = None
        
        # Filtro por envío gratis
        if free_shipping:
            # El parámetro llega como string, verificar si es 'true'
            if str(free_shipping).lower() == 'true':
                domain.append(('free_shipping', '=', True))
            # Si es 'false' o cualquier otro valor, no agregar filtro (mostrar todos)
        
        # Filtro por rango de precios predefinidos
        if price_range:
            if price_range == '0_500':
                domain.append(('discounted_price', '>', 0))
                domain.append(('discounted_price', '<=', 500))
            elif price_range == '500_1000':
                domain.append(('discounted_price', '>', 500))
                domain.append(('discounted_price', '<=', 1000))
            elif price_range == '1000_plus':
                domain.append(('discounted_price', '>', 1000))
        
        # Filtro por rango de precios personalizado (mantener para compatibilidad)
        if min_price:
            try:
                domain.append(('discounted_price', '>=', float(min_price)))
            except (ValueError, TypeError):
                min_price = None
        if max_price:
            try:
                domain.append(('discounted_price', '<=', float(max_price)))
            except (ValueError, TypeError):
                max_price = None
        
        # Filtro por descuentos (tags con descuento)
        if discount_id:
            try:
                discount_id = int(discount_id)
                domain.append(('product_tag_ids', 'in', [discount_id]))
            except (ValueError, TypeError):
                discount_id = None
        
        # Filtro por tags de promoción
        if promotion_id:
            try:
                promotion_id = int(promotion_id)
                domain.append(('product_tag_ids', 'in', [promotion_id]))
            except (ValueError, TypeError):
                promotion_id = None
        
        # Obtener productos filtrados (SOLO PUBLICADOS)
        products = request.env['product.template'].sudo().search(domain)
        
        # APLICAR ORDENAMIENTO
        if sort == 'newest':
            products = products.sorted('create_date', reverse=True)
        elif sort == 'best_sellers':
            products = products.sorted(lambda p: getattr(p, 'sales_count', 0), reverse=True)
        elif sort == 'offers':
            products = products.sorted(lambda p: (p.discount_percentage > 0 or p.fixed_discount > 0, p.discount_percentage), reverse=True)
        elif sort == 'price_low':
            products = products.sorted('list_price')
        elif sort == 'price_high':
            products = products.sorted('list_price', reverse=True)
        elif sort == 'alphabetical':
            products = products.sorted('name')
        else:  # relevance (default) - más vendidos
            products = products.sorted(lambda p: getattr(p, 'sales_count', 0), reverse=True)
        
        # Calcular precios con descuento
        for product in products:
            if product.discount_percentage > 0:
                product.discounted_price = product.list_price * (1 - product.discount_percentage / 100)
            elif product.fixed_discount > 0:
                product.discounted_price = max(0, product.list_price - product.fixed_discount)
            else:
                product.discounted_price = product.list_price
        
        # Formatear productos para la vista
        period_products = []
        for product in products:
            period_products.append({
                'product': product
            })
        
        product_count = len(products)
        
        # Obtener marcas disponibles SOLO de productos PUBLICADOS de la categoría/subcategoría seleccionada
        brand_domain = [('website_published', '=', True)]
        if category_id and not subcategory_id:
            brand_domain.append(('categ_id', 'child_of', category_id))
        elif subcategory_id:
            brand_domain.append(('categ_id', '=', subcategory_id))
        
        brand_products = request.env['product.template'].sudo().search(brand_domain)
        available_brands = brand_products.mapped('brand_type_id').filtered(
            lambda b: b.name and brand_products.filtered(lambda p: p.brand_type_id.id == b.id and p.website_published)
        )
        # Calcular contador de productos PUBLICADOS por marca
        brand_counts = {}
        for brand in available_brands:
            brand_count = len(brand_products.filtered(lambda p: p.brand_type_id.id == brand.id))
            brand_counts[brand.id] = brand_count
        
        # Obtener tags de descuento SOLO de productos PUBLICADOS de la categoría seleccionada
        if category_id or subcategory_id:
            category_products = request.env['product.template'].sudo().search(brand_domain)
            all_category_tags = category_products.mapped('product_tag_ids')
            
            discount_tags = all_category_tags.filtered(lambda t: t.is_percentage and t.discount_percentage > 0)
            promotion_tags = all_category_tags.filtered(lambda t: not t.is_percentage)
        else:
            all_published_products = request.env['product.template'].sudo().search([('website_published', '=', True)])
            category_products = all_published_products
            all_published_tags = all_published_products.mapped('product_tag_ids')
            
            discount_tags = all_published_tags.filtered(lambda t: t.is_percentage and t.discount_percentage > 0)
            promotion_tags = all_published_tags.filtered(lambda t: not t.is_percentage)
        
        # Calcular rangos de precios
        price_range_domain = brand_domain.copy()
        if free_shipping:
            price_range_domain.append(('free_shipping', '=', True))
        
        range_products = request.env['product.template'].sudo().search(price_range_domain)
        
        # Calcular precios con descuento para rangos
        for product in range_products:
            if product.discount_percentage > 0:
                product.discounted_price = product.list_price * (1 - product.discount_percentage / 100)
            elif product.fixed_discount > 0:
                product.discounted_price = max(0, product.list_price - product.fixed_discount)
            else:
                product.discounted_price = product.list_price
        
        price_ranges = {
            '0_500': len(range_products.filtered(lambda p: 0 < p.discounted_price <= 500)),
            '500_1000': len(range_products.filtered(lambda p: 500 < p.discounted_price <= 1000)),
            '1000_plus': len(range_products.filtered(lambda p: p.discounted_price > 1000)),
        }
        
        # AGREGAR PRODUCT_COUNT A LOS TAGS
        discount_tag_counts = {}
        promotion_tag_counts = {}
        
        for tag in discount_tags:
            count = len(category_products.filtered(lambda p: tag in p.product_tag_ids))
            discount_tag_counts[tag.id] = count
        
        for tag in promotion_tags:
            count = len(category_products.filtered(lambda p: tag in p.product_tag_ids))
            promotion_tag_counts[tag.id] = count
        
        values = {
            'categories': categories,
            'subcategories': subcategories,
            'selected_category': selected_category,
            'selected_subcategory': selected_subcategory,
            'selected_brand': selected_brand,
            'available_brands': available_brands,
            'brand_counts': brand_counts,
            'products': products,
            'period_products': period_products,
            'product_count': product_count,
            'discount_tags': discount_tags,
            'promotion_tags': promotion_tags,
            'discount_tag_counts': discount_tag_counts,  # Agregar diccionario
            'promotion_tag_counts': promotion_tag_counts,  # Agregar diccionario
            'price_ranges': price_ranges,
            'current_filters': {
                'category_id': category_id,
                'subcategory_id': subcategory_id,
                'brand_id': brand_id,
                'free_shipping': free_shipping,
                'min_price': min_price,
                'max_price': max_price,
                'price_range': price_range,
                'discount_id': discount_id,
                'promotion_id': promotion_id,
                'sort': sort,
            }
        }
        
        return request.render('theme_xtream.website_subcategory', values)
    
    @http.route('/category/get_subcategories', type='json', auth='public', website=True)
    def get_subcategories(self, category_id):
        try:
            published_products = request.env['product.template'].sudo().search([
                ('website_published', '=', True),
                ('categ_id', 'child_of', int(category_id))
            ])
            subcategory_ids = published_products.mapped('categ_id').filtered(
                lambda c: c.parent_id.id == int(category_id)
            )
            return [{'id': subcat.id, 'name': subcat.name} for subcat in subcategory_ids]
        except (ValueError, TypeError):
            return []
    
    @http.route('/category/get_brands', type='json', auth='public', website=True)
    def get_brands(self, category_id=None, subcategory_id=None):
        domain = [('website_published', '=', True)]
        try:
            if subcategory_id:
                domain.append(('categ_id', '=', int(subcategory_id)))
            elif category_id:
                domain.append(('categ_id', 'child_of', int(category_id)))
            
            products = request.env['product.template'].sudo().search(domain)
            brands = products.mapped('brand_type_id').filtered(lambda b: b.name)
            
            result = []
            for brand in brands:
                brand_count = len(products.filtered(lambda p: p.brand_type_id.id == brand.id))
                result.append({
                    'id': brand.id,
                    'name': brand.name,
                    'product_count': brand_count
                })
            return result
        except (ValueError, TypeError):
            return []