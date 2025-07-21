from odoo.addons.website.controllers.main import Website
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from datetime import datetime
import logging
import unicodedata
import re
_logger = logging.getLogger(__name__)

class ShopController(WebsiteSale):

    @http.route([
            '/shop/<string:product_slug>'
        ], type='http', auth="public", website=True, sitemap=False)
    def product_page_simple(self, product_slug, **kwargs):
        # Redirigir si hay parámetros adicionales en la URL
        if 'product' in kwargs:
            return request.redirect(f'/shop/{product_slug}')
        
        # Buscar el producto por slug
        product_template = request.env['product.template'].sudo().search([
            ('website_slug', '=', product_slug)
        ], limit=1)
        if not product_template.exists():
            _logger.warning(f"El producto template con slug '{product_slug}' no existe.")
            return request.not_found()
    
        # Obtener la variante principal del producto (product.product)
        product_variant = product_template.product_variant_id
        if not product_variant.exists():
            _logger.warning(f"No se encontró una variante para el producto template con slug '{product_slug}'.")
            return request.not_found()
    
        # Registrar el producto en el historial
        if request.env.user.id:
            visitor = request.env['website.visitor']._get_visitor_from_request()
            if visitor:
                try:
                    request.env['website.track'].sudo().create({
                        'visitor_id': visitor.id,
                        'product_id': product_variant.id,
                        'visit_datetime': datetime.now()
                    })
                except Exception as e:
                    _logger.error(f"Error al registrar el producto visto: {e}")
    
        product_sudo = product_template.sudo()
        _logger.info("Producto cargado: %s", product_sudo)
    
        categories = []
        categ = product_sudo.categ_id
        while categ:
            categories.insert(0, categ)
            categ = categ.parent_id
    
        referer = request.httprequest.headers.get('Referer')
        if not referer or referer == request.httprequest.url:
            referer = '/subcategory'
    
        list_price = product_sudo.list_price if product_sudo.list_price is not None else 0
        discounted_price = list_price
        if hasattr(product_sudo, 'discounted_price') and product_sudo.discounted_price is not None:
            discounted_price = product_sudo.discounted_price
        elif hasattr(product_sudo, 'standard_price') and product_sudo.standard_price is not None and list_price > product_sudo.standard_price:
            discounted_price = product_sudo.standard_price
    
        fixed_discount = 0
        discount_percentage = 0
        if list_price > discounted_price:
            fixed_discount = list_price - discounted_price
            discount_percentage = int(100 * fixed_discount / list_price)
    
        general_images = request.env['banner.image.line'].search([
            ('name', '=', 'metodos de pago'),
            ('is_active_carousel', '=', True)
        ])
    
        brand_type_products_count = 0
        if product_sudo.brand_type_id:
            brand_type_products_count = request.env['product.template'].sudo().search_count([
                ('brand_type_id', '=', product_sudo.brand_type_id.id),
                ('id', '!=', product_sudo.id),
                ('website_published', '=', True)
            ])
    
        context = {
            'product': product_sudo,
            'categories': categories,
            'referer': referer,
            'discounted_price': discounted_price,
            'discount_percentage': discount_percentage,
            'fixed_discount': fixed_discount,
            'list_price': product_sudo.list_price,
            'general_images': general_images,
            'brand_type_products_count': brand_type_products_count,
        }
        return request.render("theme_xtream.website_view_product_xtream", {
            'product': product_template,
            'product_variant': product_variant,
        })