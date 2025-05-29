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
                     discount_id=None, tag_id=None, **kw):
            """
            Renderiza la página de categoría con filtros dinámicos.
            """
            # Obtener todas las categorías principales
            categories = request.env['product.category'].sudo().search([
                ('parent_id', '=', False)
            ])
            
            # Construir dominio de búsqueda para productos
            domain = [('website_published', '=', True)]
            
            # Filtro por categoría
            if category_id:
                category_id = int(category_id)
                domain.append(('categ_id', 'child_of', category_id))
                selected_category = request.env['product.category'].sudo().browse(category_id)
                # Buscar subcategorías que tengan esta categoría como padre
                subcategories = request.env['product.category'].sudo().search([
                    ('parent_id', '=', category_id)
                ])
            else:
                selected_category = None
                subcategories = []
            
            # Filtro por subcategoría
            if subcategory_id:
                subcategory_id = int(subcategory_id)
                domain.append(('categ_id', '=', subcategory_id))
                selected_subcategory = request.env['product.category'].sudo().browse(subcategory_id)
            else:
                selected_subcategory = None
            
            # Filtro por marca
            if brand_id:
                brand_id = int(brand_id)
                domain.append(('brand_type_id', '=', brand_id))
                selected_brand = request.env['brand.type'].sudo().browse(brand_id)
            else:
                selected_brand = None
            
            # Filtro por envío gratis
            if free_shipping:
                domain.append(('free_shipping', '=', True))
            
            # Filtro por rango de precios
            if min_price:
                domain.append(('list_price', '>=', float(min_price)))
            if max_price:
                domain.append(('list_price', '<=', float(max_price)))
            
            # Filtro por descuentos
            if discount_id:
                discount_id = int(discount_id)
                domain.append(('product_tag_ids', 'in', [discount_id]))
            
            # Filtro por tags de promoción
            if tag_id:
                tag_id = int(tag_id)
                domain.append(('product_tag_ids', 'in', [tag_id]))
            
            # Obtener productos filtrados
            products = request.env['product.template'].sudo().search(domain)
            
            # Formatear productos para la vista
            period_products = []
            for product in products:
                period_products.append({
                    'product': product
                })
            
            product_count = len(products)
            
            # Obtener marcas disponibles
            if category_id or subcategory_id:
                brand_domain = [('website_published', '=', True)]
                if category_id:
                    brand_domain.append(('categ_id', 'child_of', category_id))
                if subcategory_id:
                    brand_domain.append(('categ_id', '=', subcategory_id))
                brand_products = request.env['product.template'].sudo().search(brand_domain)
                available_brands = brand_products.mapped('brand_type_id')
            else:
                available_brands = request.env['brand.type'].sudo().search([])
            
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
                    'tag_id': tag_id,
                }
            }
            
            return request.render('theme_xtream.website_subcategory', values)
        
        @http.route('/category/get_subcategories', type='json', auth='public', website=True)
        def get_subcategories(self, category_id):
            subcategories = request.env['product.category'].sudo().search([
                ('parent_id', '=', int(category_id))
            ])
            return [{'id': subcat.id, 'name': subcat.name} for subcat in subcategories]
        
        @http.route('/category/get_brands', type='json', auth='public', website=True)
        def get_brands(self, category_id=None, subcategory_id=None):
            domain = [('website_published', '=', True)]
            if category_id:
                domain.append(('categ_id', 'child_of', int(category_id)))
            if subcategory_id:
                domain.append(('categ_id', '=', int(subcategory_id)))
            
            products = request.env['product.template'].sudo().search(domain)
            brands = products.mapped('brand_type_id')
            
            result = []
            for brand in brands:
                brand_count = len(products.filtered(lambda p: p.brand_type_id.id == brand.id))
                result.append({
                    'id': brand.id,
                    'name': brand.name,
                    'product_count': brand_count
                })
            return result