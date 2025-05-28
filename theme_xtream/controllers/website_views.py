from odoo import http
from odoo.http import request
from datetime import datetime as Datetime
from pytz import timezone

class OffersController(http.Controller):

    @http.route('/offers', type='http', auth='public', website=True)
    def offers(self, free_shipping=False, **kwargs):
        """Renderiza la página de productos en oferta."""
    
        # Obtener el parámetro tag_id de la URL
        tag_id = kwargs.get('tag_id')
        
        # Construir el dominio base para productos en oferta
        domain = [
            ('website_published', '=', True),
            ('sale_ok', '=', True),
            '|',
            ('discount_percentage', '>', 0),
            ('fixed_discount', '>', 0)
        ]
        
        # Si se especifica un tag_id, filtrar por ese tag
        if tag_id:
            try:
                tag_id = int(tag_id)
                domain.append(('product_tag_ids', 'in', [tag_id]))
            except (ValueError, TypeError):
                # Si tag_id no es válido, ignorar el filtro
                pass
        
        # Filtro de envío gratis si está activo
        free_shipping = kwargs.get('free_shipping') == 'true'
        if free_shipping:
            domain.append(('free_shipping', '=', True))
        
        # Obtener productos filtrados
        Product = request.env['product.template']
        discounted_products = Product.search(domain)
        
        # Calcular precios con descuento
        for product in discounted_products:
            if product.discount_percentage > 0:
                product.discounted_price = product.list_price * (1 - product.discount_percentage / 100)
            elif product.fixed_discount > 0:
                product.discounted_price = max(0, product.list_price - product.fixed_discount)
            else:
                product.discounted_price = product.list_price
    
        # AHORA puedes usar discounted_products para obtener los tags
        used_tag_ids = []
        for product in discounted_products:
            used_tag_ids.extend(product.product_tag_ids.ids)
    
        # Guardar el estado de free_shipping en la sesión del usuario
        if 'free_shipping' in request.params:
            free_shipping = request.params.get('free_shipping') == 'true'
            request.session['free_shipping'] = free_shipping
        else:
            # Si no viene en los parámetros, usar el valor guardado en sesión (si existe)
            free_shipping = request.session.get('free_shipping', False)
    
        # Obtener productos filtrados
        Product = request.env['product.template']
        discounted_products = Product.search(domain)
        
        # Calcular precios con descuento Y agregar información de oferta
        for product in discounted_products:
            if product.discount_percentage > 0:
                product.discounted_price = product.list_price * (1 - product.discount_percentage / 100)
            elif product.fixed_discount > 0:
                product.discounted_price = max(0, product.list_price - product.fixed_discount)
            else:
                product.discounted_price = product.list_price
            
            # Agregar información de tipo de oferta y fecha de finalización
            product.offer_type = None
            product.offer_end_date = None
            
            # Buscar en las etiquetas del producto para determinar el tipo de oferta
            for tag in product.product_tag_ids:
                if tag.start_date and tag.end_date:
                    start = tag.start_date
                    end = tag.end_date
                    
                    # Convertir a datetime si son strings
                    if isinstance(start, str):
                        start = Datetime.fromisoformat(start)
                    if isinstance(end, str):
                        end = Datetime.fromisoformat(end)
                    
                    # Calcular duración en horas
                    duration = (end - start).total_seconds() / 3600.0
                    
                    # Determinar tipo de oferta basado en duración
                    if 23.5 <= duration <= 24.5:
                        product.offer_type = 'day'
                        product.offer_end_date = end.strftime('%Y-%m-%dT%H:%M:%S')
                        break
                    elif 0 < duration <= 6:
                        product.offer_type = 'flash'
                        product.offer_end_date = end.strftime('%Y-%m-%dT%H:%M:%S')
                        break
                    else:
                        product.offer_type = 'regular'
                        product.offer_end_date = end.strftime('%Y-%m-%dT%H:%M:%S')
                        break    

        
        # Aplicar filtro free_shipping si está activo
        if free_shipping:
            domain.append(('free_shipping', '=', True))
        
        # Obtener productos con etiquetas que tienen descuento real
        products = request.env['product.template'].sudo().search(domain)
        discounted_products = products.filtered(lambda p: p.list_price > p.discounted_price)
        
        # Ordenar por etiquetas y mostrar solo productos con descuento
        filtered_products = []
        for product in discounted_products:
            if product.product_tag_ids:
                filtered_products.append(product)

        
        # Obtener categorías principales (categorías sin padre)
        all_categories = request.env['product.category'].sudo().search([])
        
        # Crear el dominio para filtrar categorías
        category_domain = [
            ('website_published', '=', True),
            ('product_tag_ids', '!=', False),
        ]
        
        # Aplicar filtro de free_shipping al dominio de categorías si está activo
        if free_shipping:
            category_domain.append(('free_shipping', '=', True))
        
        main_categories = [
            cat for cat in all_categories
            if request.env['product.template'].sudo().search_count([
                *category_domain,
                ('categ_id', 'child_of', cat.id)
            ]) > 0
        ]
        
        # Solo productos publicados y que tengan al menos una etiqueta con start_date
        tagged_products = [p for p in filtered_products if p.website_published and p.product_tag_ids and p.product_tag_ids[0].start_date]
    
        # Ordenar por la fecha más reciente de start_date
        tagged_products = sorted(
            tagged_products,
            key=lambda p: p.product_tag_ids[0].start_date,
            reverse=True
        )
        product_tags = request.env['product.tag'].sudo().search([
            ('visible_on_ecommerce', '=', True)
        ], limit=6)
        
        # Resto de tu lógica existente para productos, categorías, etc.
        # ...existing code...
        
        values = {
            'product_tags': product_tags,  # Esta es la clave que falta
            # ...otros valores que ya tengas...
        }
                
        # Calcular el total de productos publicados y con etiqueta
        total_domain = [
            ('website_published', '=', True),
            ('product_tag_ids', '!=', False)
        ]
        if free_shipping:
            total_domain.append(('free_shipping', '=', True))
            
        total_products = request.env['product.template'].sudo().search_count(total_domain)
        
        oferta_dia = []
        oferta_relampago = []       
        for p in tagged_products:
            for tag in p.product_tag_ids:
                if tag.start_date and tag.end_date:
                    start = tag.start_date
                    end = tag.end_date
                    if isinstance(start, str):
                        start = Datetime.fromisoformat(start)
                    if isinstance(end, str):
                        end = Datetime.fromisoformat(end)
                    duration = (end - start).total_seconds() / 3600.0
                    if 23.5 <= duration <= 24.5:
                        oferta_dia.append(p)
                        break  # Ya cumple, no revises más etiquetas
                    elif 0 < duration <= 6:
                        oferta_relampago.append(p)
                        break

                                
        # Actualizar los contadores de rango de precios según el filtro de free_shipping
        price_range_domain = [
            ('website_published', '=', True),
            ('product_tag_ids', '!=', False),
        ]
        
        if free_shipping:
            price_range_domain.append(('free_shipping', '=', True))

        # Obtener todos los productos y filtrar por descuento real
        all_products = request.env['product.template'].sudo().search(price_range_domain)
        discounted_products = all_products.filtered(lambda p: p.list_price > p.discounted_price)
        
        # Filtrar ofertas del día y relámpago solo con productos que tengan descuento
        oferta_dia = [p for p in oferta_dia if p.list_price > p.discounted_price]        
        oferta_relampago = [p for p in oferta_relampago if p.list_price > p.discounted_price]         

        # SOLO UNA definición de price_ranges - ELIMINA TODAS LAS OTRAS
        price_ranges = {
            '0_500': len(discounted_products.filtered(lambda p: 0 < p.discounted_price <= 500)),
            '500_1000': len(discounted_products.filtered(lambda p: 500 < p.discounted_price <= 1000)),
            '1000_plus': len(discounted_products.filtered(lambda p: p.discounted_price > 1000)),
        }
        
        # Obtener categorías con conteo correcto
        categories_with_count = []
        for cat in main_categories:
            cat_domain = [
                ('website_published', '=', True),
                ('product_tag_ids', '!=', False),
                ('categ_id', 'child_of', cat.id)
            ]
            
            if free_shipping:
                cat_domain.append(('free_shipping', '=', True))
                
            # Obtener productos de la categoría y filtrar por descuento real
            cat_products = request.env['product.template'].sudo().search(cat_domain)
            cat_products_with_discount = cat_products.filtered(lambda p: p.list_price > p.discounted_price)
            prod_count = len(cat_products_with_discount)
            
            if prod_count > 0:
                categories_with_count.append({
                    'id': cat.id,
                    'name': cat.name,
                    'product_count': prod_count,
                })

        # Calcular total correcto
        all_total_products = request.env['product.template'].sudo().search(total_domain)
        total_products_with_discount = all_total_products.filtered(lambda p: p.list_price > p.discounted_price)
        
        return request.render('theme_xtream.offers_template', {
            'discounted_products': filtered_products,
            'categories_with_count': categories_with_count,
            'total_products': len(total_products_with_discount),  # Usar el conteo correcto
            'price_ranges': price_ranges,
            'oferta_dia': oferta_dia,
            'oferta_relampago': oferta_relampago,
            'all_categories': main_categories,
            'free_shipping': free_shipping,
            'product_tags': product_tags,
            'selected_tag_id': tag_id,  # Para mostrar cuál tag está seleccionado

        })
        


    @http.route(['/shop/category/<model("product.public.category"):category>', '/shop/category/all'], type='http', auth="public", website=True)
    def shop_by_category(self, category=None, **kwargs):
        """Renderiza productos filtrados por categoría y ofertas."""
        offers = kwargs.get('offers', 'false').lower() == 'true'
        free_shipping = kwargs.get('free_shipping', 'false').lower() == 'true'
        offer_type = kwargs.get('type')
        min_price = kwargs.get('min_price')
        max_price = kwargs.get('max_price')
        type_offer = request.params.get('type')
    
        # Guardar el estado de free_shipping en la sesión del usuario
        # para mantenerlo entre diferentes páginas y filtros
        if 'free_shipping' in kwargs:
            request.session['free_shipping'] = free_shipping
        else:
            # Si no viene en los parámetros, usar el valor guardado en sesión (si existe)
            free_shipping = request.session.get('free_shipping', False)
    
        domain = [
            ('website_published', '=', True),
            ('product_tag_ids', '!=', False)
        ]
        
        # Aplicar filtro de free_shipping si está activo
        if free_shipping:
            domain.append(('free_shipping', '=', True))
        
        # Crear dominio para categorías
        category_domain = [
            ('website_published', '=', True),
            ('product_tag_ids', '!=', False),
        ]
        
        if free_shipping:
            category_domain.append(('free_shipping', '=', True))
        
        # Solo mostrar categorías principales que tengan productos según los filtros actuales
        all_categories = request.env['product.category'].sudo().search([])
        main_categories = [
            cat for cat in all_categories
            if request.env['product.template'].sudo().search_count([
                *category_domain,
                ('categ_id', 'child_of', cat.id)
            ]) > 0
        ]
        product_tags = request.env['product.tag'].sudo().search([
            ('visible_on_ecommerce', '=', True)  # Solo los visibles en ecommerce
        ], limit=6)

        categories_with_count = []
        for cat in main_categories:
            cat_domain = [
                ('website_published', '=', True),
                ('product_tag_ids', '!=', False),
                ('categ_id', 'child_of', cat.id)
            ]
            
            if free_shipping:
                cat_domain.append(('free_shipping', '=', True))
                
            # Obtener productos de la categoría y filtrar por descuento real
            cat_products = request.env['product.template'].sudo().search(cat_domain)
            cat_products_with_discount = cat_products.filtered(lambda p: p.list_price > p.discounted_price)
            prod_count = len(cat_products_with_discount)
            
            if prod_count > 0:  # Solo incluir categorías con productos que cumplan el filtro
                categories_with_count.append({
                    'id': cat.id,
                    'name': cat.name,
                    'product_count': prod_count,
                })
                    
        category_id = request.params.get('category_id')
        if category_id:
            domain.append(('categ_id', 'child_of', int(category_id)))
        
        if offers:
            domain.append(('discounted_price', '>', 0))
        
        if offer_type:
            tag = request.env['product.tag'].sudo().search([('name', 'ilike', offer_type)], limit=1)
            if tag:
                domain.append(('product_tag_ids', 'in', tag.id))
        
        if min_price:
            domain.append(('discounted_price', '>=', float(min_price)))
        
        if max_price:
            domain.append(('discounted_price', '<=', float(max_price)))
    
        # IMPORTANTE: Primero BUSCAR los productos
        products = request.env['product.template'].sudo().search(domain)
        
        # Agregar información de tipo de oferta para cada producto
        for product in products:
            # Agregar información de tipo de oferta y fecha de finalización
            product.offer_type = None
            product.offer_end_date = None
            
            # Buscar en las etiquetas del producto para determinar el tipo de oferta
            for tag in product.product_tag_ids:
                if tag.start_date and tag.end_date:
                    start = tag.start_date
                    end = tag.end_date
                    
                    # Convertir a datetime si son strings
                    if isinstance(start, str):
                        start = Datetime.fromisoformat(start)
                    if isinstance(end, str):
                        end = Datetime.fromisoformat(end)
                    
                    # Calcular duración en horas
                    duration = (end - start).total_seconds() / 3600.0
                    
                    # Determinar tipo de oferta basado en duración
                    if 23.5 <= duration <= 24.5:
                        product.offer_type = 'day'
                        product.offer_end_date = end.strftime('%Y-%m-%dT%H:%M:%S')
                        break
                    elif 0 < duration <= 6:
                        product.offer_type = 'flash'
                        product.offer_end_date = end.strftime('%Y-%m-%dT%H:%M:%S')
                        break
                    else:
                        product.offer_type = 'regular'
                        product.offer_end_date = end.strftime('%Y-%m-%dT%H:%M:%S')
                        break    
    
        # LUEGO filtrar por descuento real
        products = products.filtered(lambda p: p.list_price > p.discounted_price)
        
        
        # Si estás procesando tiempos restantes, mantener solo productos con descuento real
        if type_offer in ['day', 'flash', 'current']:
        
            filtered = []
            remaining_times = {}  # Diccionario para almacenar los tiempos restantes
            now = Datetime.now(timezone('America/Mexico_City'))
            
            for p in products:
                for tag in p.product_tag_ids:
                    if tag.start_date and tag.end_date:
                        start = tag.start_date
                        end = tag.end_date
                        if isinstance(start, str):
                            start = Datetime.fromisoformat(start)
                        if isinstance(end, str):
                            end = Datetime.fromisoformat(end)
                        
                        # Convertir a objetos datetime conscientes de la zona horaria
                        if start.tzinfo is None:
                            start = start.replace(tzinfo=timezone('UTC'))
                            start = start.astimezone(timezone('America/Mexico_City'))
                        if end.tzinfo is None:
                            end = end.replace(tzinfo=timezone('UTC'))
                            end = end.astimezone(timezone('America/Mexico_City'))
                        
                        duration = (end - start).total_seconds() / 3600.0
                        
                        if type_offer == 'day' and 23.5 <= duration <= 24.5:
                            filtered.append(p)
                            break  # Ya cumple, no revises más etiquetas
                        elif type_offer == 'flash' and 0 < duration <= 6:
                            filtered.append(p)
                            break
                        elif type_offer == 'current' and start <= now <= end:
                            # Para ofertas activas actualmente
                            filtered.append(p)
                            # Calcular tiempo restante
                            remaining_time = end - now
                            remaining_hours = int(remaining_time.total_seconds() / 3600)
                            remaining_minutes = int((remaining_time.total_seconds() % 3600) / 60)
                            # Almacenar en el diccionario usando el ID del producto como clave
                            remaining_times[p.id] = f"{remaining_hours}h {remaining_minutes}m"
                            break
            products = filtered
    
        # Calcular el total de productos según los filtros actuales
        total_domain = [
            ('website_published', '=', True),
            ('product_tag_ids', '!=', False)
        ]
        
        if free_shipping:
            total_domain.append(('free_shipping', '=', True))
            
        total_products = request.env['product.template'].sudo().search_count(total_domain)
    
        # Actualizar los contadores de rango de precios según el filtro de free_shipping
        price_range_domain = [
            ('website_published', '=', True),
            ('product_tag_ids', '!=', False),
        ]
        
        if free_shipping:
            price_range_domain.append(('free_shipping', '=', True))

        # Obtener todos los productos y filtrar por descuento real
        all_products = request.env['product.template'].sudo().search(price_range_domain)
        discounted_products = all_products.filtered(lambda p: p.list_price > p.discounted_price)
        
        # SOLO UNA definición de price_ranges - ELIMINA LA DUPLICADA
        price_ranges = {
            '0_500': len(discounted_products.filtered(lambda p: 0 < p.discounted_price <= 500)),
            '500_1000': len(discounted_products.filtered(lambda p: 500 < p.discounted_price <= 1000)),
            '1000_plus': len(discounted_products.filtered(lambda p: p.discounted_price > 1000)),
        }

        # Calcular total correcto
        all_total_products = request.env['product.template'].sudo().search(total_domain)
        total_products_with_discount = all_total_products.filtered(lambda p: p.list_price > p.discounted_price)
    
        return request.render('theme_xtream.offers_template', {
            'discounted_products': products,
            'current_category': category,
            'offers': offers,
            'free_shipping': free_shipping,
            'total_products': len(total_products_with_discount),  # Usar el conteo correcto
            'price_ranges': price_ranges,
            'offer_type': offer_type,
            'categories_with_count': categories_with_count,
            'all_categories': main_categories,
            'product_tags': product_tags,
        })