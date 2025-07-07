from odoo import http
from odoo.http import request

class CategoryController(http.Controller):

    @http.route('/category', auth='public', website=True)
    def home(self):
        return http.request.render('theme_xtream.website_category')  

    @http.route('/subcategory', auth='public', website=True)
    def category(self, category_id=None, subcategory_id=None, brand_id=None, 
                 free_shipping=None, min_price=None, max_price=None, price_range=None,
                 discount_id=None, promotion_id=None, sort=None, search=None, **kw):
        """
        Renderiza la página de subcategoría con filtros dinámicos.
        SOLO productos publicados aparecerán en marcas, categorías, ofertas y rangos de precio.
        """
        # Obtener todas las categorías principales QUE TENGAN PRODUCTOS PUBLICADOS
        published_products_categories = request.env['product.template'].sudo().search([
            ('website_published', '=', True),
            ('qty_available', '>', 0)
        ]).mapped('categ_id')
        
        categories = request.env['product.category'].sudo().search([
            ('parent_id', '=', False),
            ('id', 'in', published_products_categories.ids)
        ])
        
        # Construir dominio base SOLO para productos publicados (sin filtros de precio)
        domain = [('website_published', '=', True), ('qty_available', '>', 0)]
        
        # Variables para la vista
        selected_category = None
        selected_subcategory = None
        selected_brand = None
        subcategories = []
        
        if search:
            domain.append(('name', 'ilike', search))

        # Filtro por categoría (ESTE ES EL PRINCIPAL)
        if category_id:
            try:
                category_id = int(category_id)
                domain.append(('categ_id', 'child_of', category_id))
                selected_category = request.env['product.category'].sudo().browse(category_id)
                
                # Buscar subcategorías QUE TENGAN PRODUCTOS PUBLICADOS
                category_published_products = request.env['product.template'].sudo().search([
                    ('website_published', '=', True),
                    ('categ_id', 'child_of', category_id),
                    ('qty_available', '>', 0)
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
                domain.append(('categ_id', 'child_of', subcategory_id))
                # domain.append(('categ_id', '=', subcategory_id))
                selected_subcategory = request.env['product.category'].sudo().browse(subcategory_id)
            except (ValueError, TypeError):
                subcategory_id = None
        
        selected_subcategory_children = []
        if selected_subcategory:
            selected_subcategory_children = request.env['product.category'].sudo().search([('parent_id', '=', selected_subcategory.id)])
        
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
            if str(free_shipping).lower() == 'true':
                domain.append(('free_shipping', '=', True))
        
        # Filtro por descuentos (tags con descuento)
        if discount_id:
            try:
                discount_id = int(discount_id)
                domain.append(('discount_percentage', '=', discount_id))  # Solo ese %
            except ValueError:
                pass
        
        # Filtro por tags de promoción
        if promotion_id:
            try:
                promotion_id = int(promotion_id)
                domain.append(('product_tag_ids', 'in', [promotion_id]))
            except (ValueError, TypeError):
                promotion_id = None

        # Obtener productos filtrados (SOLO PUBLICADOS, sin filtro de precio)
        products = request.env['product.template'].sudo().search(domain)

        # Calcular precios con descuento
        for product in products:
            if product.discount_percentage > 0:
                product.discounted_price = product.list_price * (1 - product.discount_percentage / 100)
            elif product.fixed_discount > 0:
                product.discounted_price = max(0, product.list_price - product.fixed_discount)
            else:
                product.discounted_price = product.list_price

        # Filtro de precio en Python (NO en el dominio)
        if price_range:
            if price_range == '0_500':
                products = products.filtered(lambda p: 0 < p.discounted_price <= 500)
            elif price_range == '500_1000':
                products = products.filtered(lambda p: 500 < p.discounted_price <= 1000)
            elif price_range == '1000_plus':
                products = products.filtered(lambda p: p.discounted_price > 1000)
        if min_price:
            try:
                min_price_val = float(min_price)
                products = products.filtered(lambda p: p.discounted_price >= min_price_val)
            except Exception:
                pass
        if max_price:
            try:
                max_price_val = float(max_price)
                products = products.filtered(lambda p: p.discounted_price <= max_price_val)
            except Exception:
                pass

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

        # Formatear productos para la vista
        period_products = []
        for product in products:
            period_products.append({
                'product': product
            })

        forced_brand_names = [
            'EPCOM PROFESSIONAL',
            'HiLook by HIKVISION',
            'ADEMCO (HONEYWELL)',
            'HIKVISION',
            'EZVIZ'
        ]

        # Obtener marcas disponibles SOLO de productos PUBLICADOS de la categoría/subcategoría seleccionada
        brand_domain = domain.copy()
        brand_domain = [d for d in brand_domain if d[0] != 'brand_type_id']
        brand_products = request.env['product.template'].sudo().search(brand_domain + [('qty_available', '>', 0)])
        available_brands = brand_products.mapped('brand_type_id').filtered(
            lambda b: b.name and brand_products.filtered(lambda p: p.brand_type_id.id == b.id)
        )

        forced_brands = []
        other_brands = []
        for name in forced_brand_names:
            brand = next((b for b in available_brands if b.name == name), None)
            if brand:
                forced_brands.append(brand)
        for brand in available_brands:
            if brand.name not in forced_brand_names:
                other_brands.append(brand)
        
        product_count = len(products)

        # Calcular contador de productos PUBLICADOS por marca, usando los mismos filtros
        brand_counts = {}
        for brand in available_brands:
            count = len(brand_products.filtered(lambda p: p.brand_type_id.id == brand.id))
            brand_counts[brand.id] = count

        # Obtener tags de descuento SOLO de productos PUBLICADOS de la categoría seleccionada
        if category_id or subcategory_id:
            category_products = request.env['product.template'].sudo().search(brand_domain + [('qty_available', '>', 0)])
            all_category_tags = category_products.mapped('product_tag_ids')
            discount_tags = all_category_tags.filtered(lambda t: t.is_percentage and t.discount_percentage > 0)
            promotion_tags = all_category_tags.filtered(lambda t: not t.is_percentage)
        else:
            all_published_products = request.env['product.template'].sudo().search([('website_published', '=', True)])
            category_products = all_published_products
            all_published_tags = all_published_products.mapped('product_tag_ids')
            discount_tags = all_published_tags.filtered(lambda t: t.is_percentage and t.discount_percentage > 0)
            promotion_tags = all_published_tags.filtered(lambda t: not t.is_percentage)

        # Calcular rangos de precios (para los contadores)
        price_range_domain = domain.copy()
        # Si tienes algún filtro de precio en domain, quítalo aquí (en tu caso, no hay porque los aplicas en Python)
        if free_shipping:
            price_range_domain.append(('free_shipping', '=', True))
        range_products = request.env['product.template'].sudo().search(price_range_domain)
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

        try:
            current_page = int(request.params.get('page', 1))
        except Exception:
            current_page = 1

        per_page = 5
        total_products = len(period_products)
        total_pages = max(1, (total_products + per_page - 1) // per_page)
        start = (current_page - 1) * per_page
        end = start + per_page
        period_products = period_products[start:end]

        # Obtener los valores únicos de discount_percentage de los tags activos con is_percentage=True
        discount_ranges = sorted({
            tag.discount_percentage
            for tag in request.env['product.tag'].sudo().search([
            ('is_active', '=', True),
            ('is_percentage', '=', True),
            ('discount_percentage', '>', 0)
            ])
            if tag.discount_percentage
        })
        discount_tags = []
        discount_tag_counts = {}
        discount_tag_counts_general = {}

        for percent in discount_ranges:
            domain_with_filters = domain.copy()
            domain_with_filters.append(('discount_percentage', '=', percent))
            count = request.env['product.template'].sudo().search_count(domain_with_filters)
            count_general = request.env['product.template'].sudo().search_count([
                ('website_published', '=', True),
                ('discount_percentage', '=', percent),
            ])
            if count_general > 0:
                tag = {
                    'id': percent,
                    'name': f'Desde {percent}% OFF'
                }
                discount_tags.append(tag)
                discount_tag_counts[percent] = count
                discount_tag_counts_general[percent] = count_general

        # --- PROMOCIONES ---
        promotion_tag_objs = request.env['product.tag'].sudo().search([('is_active', '=', True)])
        promotion_tags = []
        promotion_tag_counts = {}
        promotion_tag_counts_general = {}

        for tag in promotion_tag_objs:
            domain_with_filters = domain.copy()
            domain_with_filters.append(('product_tag_ids', 'in', tag.id))
            count = request.env['product.template'].sudo().search_count(domain_with_filters)
            count_general = request.env['product.template'].sudo().search_count([
                ('website_published', '=', True),
                ('product_tag_ids', 'in', tag.id),
            ])
            if count_general > 0:
                promotion_tags.append(tag)
                promotion_tag_counts[tag.id] = count
                promotion_tag_counts_general[tag.id] = count_general

        values = {
            'categories': categories,
            'current_page': current_page,
            'total_pages': total_pages,
            'forced_brands': forced_brands,
            'other_brands': other_brands,
            'product_count': product_count,
            'selected_subcategory_children': selected_subcategory_children,
            'discount_tags': discount_tags,
            'discount_tag_counts': discount_tag_counts,
            'discount_tag_counts_general': discount_tag_counts_general,
            'promotion_tags': promotion_tags,
            'promotion_tag_counts': promotion_tag_counts,
            'promotion_tag_counts_general': promotion_tag_counts_general,
            'subcategories': subcategories,
            'selected_category': selected_category,
            'selected_subcategory': selected_subcategory,
            'selected_brand': selected_brand,
            'available_brands': available_brands,
            'brand_counts': brand_counts,
            'products': products,
            'period_products': period_products,
            'product_count': product_count,
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
        
    @http.route('/category_search', auth='public', website=True)
    def category_search(self, search=None, **kwargs):
        # Mostrar siempre todas las categorías visibles en menú
        categories = request.env['product.category'].sudo().search([
            ('is_visible_in_menu', '=', True)
        ])
        
        products = []
        category = None
        brands = []
        product_tags = []
    
        if search:
            # Buscar productos por nombre o modelo
            products = request.env['product.template'].sudo().search([
                '|',  # Condición OR
                ('name', 'ilike', search),
                ('product_model', 'ilike', search)
            ])
            
            # Buscar categorías relacionadas con el término de búsqueda
            searched_categories = request.env['product.category'].sudo().search([
                '|',
                ('name', 'ilike', search),
                ('slug', '=', search.lower().replace(' ', '-'))
            ])
            if searched_categories:
                category = searched_categories[0]
                # Solo marcas de productos publicados en esa categoría (y subcategorías)
                products_in_cat = request.env['product.template'].sudo().search([
                    ('website_published', '=', True),
                    ('categ_id', 'child_of', category.id)
                ])
                brands = products_in_cat.mapped('brand_type_id').filtered(lambda b: b.icon_image and b.active)
                product_tags = products_in_cat.mapped('product_tag_ids').filtered(lambda t: t.is_active)
        else:
            brands = request.env['brand.type'].sudo().search([
                ('icon_image', '!=', False),
                ('active', '=', True)
            ])
            product_tags = request.env['product.tag'].sudo().search([
                ('is_active', '=', True)
            ])
    
        values = {
            'search': search,
            'categories': categories,
            'category': category,
            'products': products,
            'brands': brands,
            'product_tags': product_tags,
        }
        return request.render('theme_xtream.category_search', values)
    
    @http.route('/category/<string:slug>', auth='public', website=True)
    def category_by_slug(self, slug, **kwargs):
        # Buscar la categoría por slug
        category = request.env['product.category'].sudo().search([('slug', '=', slug)], limit=1)
        if not category:
            return request.not_found()

        # Buscar productos publicados en esa categoría (y subcategorías)
        products = request.env['product.template'].sudo().search([
            ('website_published', '=', True),
            ('categ_id', 'child_of', category.id)
        ])

        # Puedes agregar más lógica de filtros, paginación, etc. si lo necesitas

        values = {
            'category': category,
            'products': products,
        }
        return request.render('theme_xtream.category_search', values)