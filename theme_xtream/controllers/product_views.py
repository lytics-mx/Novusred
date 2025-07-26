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
            '/product/<string:product_name>/<int:product_id>'
        ], type='http', auth="public", website=True, sitemap=False)
    def product_page_simple(self, product_name, product_id, **kwargs):
        # Obtener el producto template
        product_template = request.env['product.template'].sudo().browse(product_id)
        if not product_template.exists():
            _logger.warning(f"El producto template con ID {product_id} no existe.")
            return request.not_found()

        # Validar que el nombre del producto en la URL coincida con el nombre real
        expected_name = product_template.name.replace(' ', '-').lower()
        if product_name != expected_name:
            return request.redirect(f'/product/{expected_name}/{product_id}')
        
        # Obtener la variante principal del producto (product.product)
        product_variant = product_template.product_variant_id
        if not product_variant.exists():
            _logger.warning(f"No se encontró una variante para el producto template con ID {product_id}.")
            return request.not_found()
    
        # Registrar el producto en el historial
        if request.env.user.id:
            visitor = request.env['website.visitor']._get_visitor_from_request()
            if visitor:
                try:
                    request.env['website.track'].sudo().create({
                        'visitor_id': visitor.id,
                        'product_id': product_variant.id,  # Usar el ID de la variante
                        'visit_datetime': datetime.now()
                    })
                except Exception as e:
                    _logger.error(f"Error al registrar el producto visto: {e}")
    
        # Obtener el producto con sudo para evitar problemas de permisos
        product_sudo = product_template.sudo()
        _logger.info("Producto cargado: %s", product_sudo)
    
        # Obtener la jerarquía de categorías
        categories = []
        categ = product_sudo.categ_id
        while categ:
            categories.insert(0, categ)
            categ = categ.parent_id
    
        # Obtener la URL de referencia (página anterior)
        referer = request.httprequest.headers.get('Referer')
        if not referer or referer == request.httprequest.url:
            referer = '/subcategory'
    
        # Cálculo de descuentos (ejemplo)
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
    
        # Calcular el contador de productos publicados y disponibles por cada marca en available_brands
        brand_type_products_count = 0
        if product_sudo.brand_type_id:
            brand_type_products_count = request.env['product.template'].sudo().search_count([
                ('brand_type_id', '=', product_sudo.brand_type_id.id),
                ('id', '!=', product_sudo.id),
                ('website_published', '=', True)
            ])
    
        context = {
            'product': product_sudo,  # Usar product_sudo en lugar de product
            'categories': categories,
            'referer': referer,
            'discounted_price': discounted_price,
            'discount_percentage': discount_percentage,
            'fixed_discount': fixed_discount,
            'list_price': product_sudo.list_price,
            'general_images': general_images,
            'brand_type_products_count': brand_type_products_count,
        }
        # Renderizar la página del producto
        return request.render("theme_xtream.website_view_product_xtream", {
            'product': product_template,
            'product_variant': product_variant,
        })