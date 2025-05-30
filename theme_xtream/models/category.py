from odoo import http
from odoo.http import request

class CategoryController(http.Controller):

    @http.route('/category', auth='public', website=True)
    def home(self):
        return http.request.render('theme_xtream.website_category')  

    from odoo import http
    from odoo.http import request
    
    class CategoryController(http.Controller):
    
        @http.route('/category', auth='public', website=True)
        def home(self):
            return http.request.render('theme_xtream.website_category')  
    
        @http.route('/subcategory', auth='public', website=True)
        def category(self, category_id=None, subcategory_id=None, brand_id=None, 
                     free_shipping=None, min_price=None, max_price=None, 
                     discount_id=None, promotion_id=None, **kw):
            """
            Renderiza la página de categoría con filtros dinámicos.
            """
            # Obtener todas las categorías principales
            categories = request.env['product.category'].sudo().search([
                ('parent_id', '=', False)
            ])
            
            # Construir dominio de búsqueda para productos - EMPEZAR CON TODOS LOS PRODUCTOS
            domain = [('website_published', '=', True)]
            
            # Variables para la vista
            selected_category = None
            selected_subcategory = None
            selected_brand = None
            subcategories = []
            
            # Filtro por categoría
            if category_id:
                try:
                    category_id = int(category_id)
                    domain.append(('categ_id', 'child_of', category_id))
                    selected_category = request.env['product.category'].sudo().browse(category_id)
                    # Buscar subcategorías que tengan esta categoría como padre
                    subcategories = request.env['product.category'].sudo().search([
                        ('parent_id', '=', category_id)
                    ])
                except (ValueError, TypeError):
                    category_id = None
            
            # Filtro por subcategoría
            if subcategory_id:
                try:
                    subcategory_id = int(subcategory_id)
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
                domain.append(('free_shipping', '=', True))
            
            # Filtro por rango de precios
            if min_price:
                try:
                    domain.append(('list_price', '>=', float(min_price)))
                except (ValueError, TypeError):
                    min_price = None
            if max_price:
                try:
                    domain.append(('list_price', '<=', float(max_price)))
                except (ValueError, TypeError):
                    max_price = None
            
            # Filtro por descuentos
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
            
            # Obtener productos filtrados
            products = request.env['product.template'].sudo().search(domain, limit=50)
            
            # Formatear productos para la vista
            period_products = []
            for product in products:
                period_products.append({
                    'product': product
                })
            
            product_count = len(products)
            
            # Obtener todas las marcas disponibles (para mostrar en filtros)
            all_products = request.env['product.template'].sudo().search([('website_published', '=', True)])
            available_brands = all_products.mapped('brand_type_id').filtered(lambda b: b.name)
            
            # Si hay filtros de categoría, limitar marcas a esa categoría
            if category_id or subcategory_id:
                brand_domain = [('website_published', '=', True)]
                if category_id:
                    brand_domain.append(('categ_id', 'child_of', category_id))
                if subcategory_id:
                    brand_domain.append(('categ_id', '=', subcategory_id))
                brand_products = request.env['product.template'].sudo().search(brand_domain)
                available_brands = brand_products.mapped('brand_type_id').filtered(lambda b: b.name)
            
            # Obtener tags de descuento
            discount_tags = request.env['product.tag'].sudo().search([
                ('is_percentage', '=', True),
                ('discount_percentage', '>', 0)
            ])
            
            # Obtener tags de promoción
            promotion_tags = request.env['product.tag'].sudo().search([
                ('is_percentage', '=', False)
            ])
            
            values = {
                'categories': categories,
                'subcategories': subcategories,
                'selected_category': selected_category,
                'selected_subcategory': selected_subcategory,
                'selected_brand': selected_brand,
                'available_brands': available_brands,
                'products': products,
                'period_products': period_products,
                'product_count': product_count,
                'discount_tags': discount_tags,
                'promotion_tags': promotion_tags,
                'current_filters': {
                    'category_id': category_id,
                    'subcategory_id': subcategory_id,
                    'brand_id': brand_id,
                    'free_shipping': free_shipping,
                    'min_price': min_price,
                    'max_price': max_price,
                    'discount_id': discount_id,
                    'promotion_id': promotion_id,
                }
            }
            
            return request.render('theme_xtream.website_subcategory', values)
        
        @http.route('/category/get_subcategories', type='json', auth='public', website=True)
        def get_subcategories(self, category_id):
            try:
                subcategories = request.env['product.category'].sudo().search([
                    ('parent_id', '=', int(category_id))
                ])
                return [{'id': subcat.id, 'name': subcat.name} for subcat in subcategories]
            except (ValueError, TypeError):
                return []
        
        @http.route('/category/get_brands', type='json', auth='public', website=True)
        def get_brands(self, category_id=None, subcategory_id=None):
            domain = [('website_published', '=', True)]
            try:
                if category_id:
                    domain.append(('categ_id', 'child_of', int(category_id)))
                if subcategory_id:
                    domain.append(('categ_id', '=', int(subcategory_id)))
                
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