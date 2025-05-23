from odoo import http
from odoo.http import request
from datetime import datetime as Datetime
from pytz import timezone

class OffersController(http.Controller):

    @http.route('/offers', type='http', auth='public', website=True)
    def offers(self, **kwargs):
        """Renderiza la página de productos en oferta."""
        # Filtrar productos publicados que tengan al menos una etiqueta
        tagged_products = request.env['product.template'].sudo().search([
            ('website_published', '=', True),
            ('product_tag_ids', '!=', False)
        ])

        # Solo productos publicados y que tengan al menos una etiqueta con start_date
        tagged_products = [p for p in tagged_products if p.website_published and p.product_tag_ids and p.product_tag_ids[0].start_date]

        # Obtener las categorías de los productos en oferta
        # Obtener categorías (principales o subcategorías) que tengan productos con tags
        category_ids = set()
        for p in tagged_products:
            for cat in p.public_categ_ids:
                category_ids.add(cat.id)
                offer_categories = request.env['product.public.category'].sudo().search([
                    ('id', 'in', list(category_ids)),
                    ('product_tmpl_ids.product_tag_ids', '!=', False)
                ])
        # Ordenar por la fecha más reciente de start_date
        tagged_products = sorted(
            tagged_products,
            key=lambda p: p.product_tag_ids[0].start_date,
            reverse=True
        )
        # Calcular el total de productos publicados y con etiqueta
        total_products = request.env['product.template'].sudo().search_count([
            ('website_published', '=', True),
            ('product_tag_ids', '!=', False)
        ])
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
                   
                    
        price_ranges = {
            '0_500': request.env['product.template'].sudo().search_count([
                ('website_published', '=', True),
                ('product_tag_ids', '!=', False),
                ('discounted_price', '>', 0),
                ('discounted_price', '<=', 500)
            ]),
            '500_1000': request.env['product.template'].sudo().search_count([
                ('website_published', '=', True),
                ('product_tag_ids', '!=', False),
                ('discounted_price', '>', 500),
                ('discounted_price', '<=', 1000)
            ]),
            '1000_plus': request.env['product.template'].sudo().search_count([
                ('website_published', '=', True),
                ('product_tag_ids', '!=', False),
                ('discounted_price', '>', 1000)
            ]),
        }

        return request.render('theme_xtream.offers_template', {
            'discounted_products': tagged_products,
            'total_products': total_products,
            'price_ranges': price_ranges,
            'oferta_dia': oferta_dia,
            'oferta_relampago': oferta_relampago, 
            'offer_categories': offer_categories,           
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

        domain = [
            ('website_published', '=', True),
            ('product_tag_ids', '!=', False)
        ]
        
        if category and category.id:
            domain.append(('public_categ_ids', 'child_of', category.id))
        else:
            # Si no hay categoría, mostrar todos los productos
            domain.append(('public_categ_ids', '!=', False))

        
        if offers:
            domain.append(('discounted_price', '>', 0))
        
        if free_shipping:
            domain.append(('free_shipping', '=', True))
        
        if offer_type:
            tag = request.env['product.tag'].sudo().search([('name', 'ilike', offer_type)], limit=1)
            if tag:
                domain.append(('product_tag_ids', 'in', tag.id))
        
        if min_price:
            domain.append(('discounted_price', '>=', float(min_price)))
        
        if max_price:
            domain.append(('discounted_price', '<=', float(max_price)))
 

        # Buscar productos y categorías
        products = request.env['product.template'].sudo().search(domain)

        if type_offer in ['day', 'flash']:
            filtered = []
            for p in products:
                for tag in p.product_tag_ids:
                    if tag.start_date and tag.end_date:
                        start = tag.start_date
                        end = tag.end_date
                        if isinstance(start, str):
                            start = Datetime.fromisoformat(start)
                        if isinstance(end, str):
                            end = Datetime.fromisoformat(end)
                        duration = (end - start).total_seconds() / 3600.0
                        if type_offer == 'day' and 23.5 <= duration <= 24.5:
                            filtered.append(p)
                            break  # Ya cumple, no revises más etiquetas
                        elif type_offer == 'flash' and 0 < duration <= 6:
                            filtered.append(p)
                            break
            products = filtered


        price_ranges = {
            '0_500': request.env['product.template'].sudo().search_count([
                ('website_published', '=', True),
                ('product_tag_ids', '!=', False),
                ('discounted_price', '>', 0),
                ('discounted_price', '<=', 500)
            ]),
            '500_1000': request.env['product.template'].sudo().search_count([
                ('website_published', '=', True),
                ('product_tag_ids', '!=', False),
                ('discounted_price', '>', 500),
                ('discounted_price', '<=', 1000)
            ]),
            '1000_plus': request.env['product.template'].sudo().search_count([
                ('website_published', '=', True),
                ('product_tag_ids', '!=', False),
                ('discounted_price', '>', 1000)
            ]),
        }

        return request.render('theme_xtream.offers_template', {
            'discounted_products': products,
            'current_category': category,
            'offers': offers,
            'free_shipping': free_shipping,
            'price_ranges': price_ranges,
            'offer_type': offer_type,
        })