from odoo.addons.website.controllers.main import Website
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from werkzeug.utils import redirect
import logging
_logger = logging.getLogger(__name__)

class ShopController(WebsiteSale):

    @http.route([
        '/view/<model("product.template"):product>',
        '/view/product/<model("product.template"):product>'
    ], type='http', auth="public", website=True, csrf=False)  # <--- csrf desactivado
    def product_page(self, product, **kwargs):
        # ...existing code...
        if not product:
            return request.not_found()
        _logger.info("Producto cargado: %s", product)

        # Obtener la jerarquía de categorías
        categories = []
        categ = product.categ_id
        while categ:
            categories.insert(0, categ)
            categ = categ.parent_id

        # Obtener la URL de referencia (página anterior)
        referer = request.httprequest.headers.get('Referer')
        if not referer or referer == request.httprequest.url:
            referer = '/subcategory'
        # Cálculo de descuentos (ejemplo)
        list_price = product.list_price if product.list_price is not None else 0
        discounted_price = list_price
        if hasattr(product, 'discounted_price') and product.discounted_price is not None:
            discounted_price = product.discounted_price
        elif hasattr(product, 'standard_price') and product.standard_price is not None and list_price > product.standard_price:
            discounted_price = product.standard_price

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
        # Obtener la marca del producto actual
        brand = getattr(product, 'brand_type_id', False)
        brand_type_products_count = 0
        brand_type_name = ""
        if brand:
            brand_type_name = brand.name
            # Buscar productos publicados y disponibles de esa marca (brand.type.id)
            brand_type_products_count = request.env['product.template'].sudo().search_count([
            ('website_published', '=', True),
            ('qty_available', '>', 0),
            ('brand_type_id', '=', brand.id)
            ])

        context = {
            'product': product,
            'categories': categories,
            'referer': referer,
            'discounted_price': discounted_price,
            'discount_percentage': discount_percentage,
            'fixed_discount': fixed_discount,
            'list_price': product.list_price,  # <-- Agrega esto
            'general_images': general_images,
            'brand_type_products_count': brand_type_products_count,
            'brand_type_name': brand_type_name,
            'brand' : brand,
                 
        }
        return request.render("theme_xtream.website_view_product_xtream", context)
    
