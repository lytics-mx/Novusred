from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
import logging
_logger = logging.getLogger(__name__)

class ShopController(WebsiteSale):

    @http.route([
        '/shop/product/<model("product.template"):product>'
    ], type='http', auth="public", website=True, csrf=False)
    def product(self, product, category='', search='', **kwargs):
        return self.product_page(product, **kwargs)

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
        ])        # Calcular el contador de productos publicados y disponibles por cada marca en available_brands
        # Obtener la marca del producto actual
        brand_type_products_count = 0
        if product.brand_type_id:
            brand_type_products_count = request.env['product.template'].sudo().search_count([
                ('brand_type_id', '=', product.brand_type_id.id),
                ('id', '!=', product.id),
                ('website_published', '=', True)
            ])
        
        # Obtener qty_available de forma segura
        try:
            qty_available = product.sudo().qty_available
        except:
            qty_available = None
        
        # related_tag_products = []        # if product.product_tag_ids:
        #     related_tag_products = request.env['product.template'].sudo().search([
        #         ('product_tag_ids', 'in', product.product_tag_ids.ids),
        #         ('id', '!=', product.id),
        #         ('website_published', '=', True)
        #     ], limit=20)

       
        safe_product = product.sudo()
        context = {
            'product': safe_product,
            'categories': categories,
            'referer': referer,
            'discounted_price': discounted_price,
            'discount_percentage': discount_percentage,
            'fixed_discount': fixed_discount,
            'list_price': safe_product.list_price,
            'general_images': general_images,
            'brand_type_products_count': brand_type_products_count,
            'qty_available': qty_available,
            # 'related_tag_products': related_tag_products,
                 
        }
        
        # Agregar qty_available al product para evitar errores
        safe_product = safe_product.with_context(qty_available=qty_available)
        context['product'] = safe_product
        
        return request.render("website_sale.product", context)
