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
        # Llamar al método padre para obtener el contexto base
        result = super(ShopController, self).product(product, category, search, **kwargs)
        
        # Obtener qty_available de forma segura
        try:
            # Intentar obtener el stock con sudo() y un contexto limpio
            product_sudo = product.sudo().with_context(
                warehouse=False,
                location=False,
                force_company=request.env.company.id
            )
            qty_available = product_sudo.qty_available
        except Exception as e:
            _logger.info("No se pudo obtener qty_available: %s", e)
            qty_available = None
        
        # Actualizar el contexto con el valor seguro
        if hasattr(result, 'qcontext'):
            result.qcontext['qty_available'] = qty_available
            # También crear una versión del producto que no cause errores
            safe_product = product.sudo()
            # Monkey patch para evitar el error en qty_available
            def safe_qty_available(self):
                return qty_available if qty_available is not None else 0
            
            # Reemplazar el método problemático temporalmente
            original_method = safe_product.__class__.qty_available
            safe_product.__class__.qty_available = property(safe_qty_available)
            result.qcontext['product'] = safe_product
        
        return result

    @http.route([
        '/view/<model("product.template"):product>',
        '/view/product/<model("product.template"):product>'
    ], type='http', auth="public", website=True, csrf=False)
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
        
        # Calcular el contador de productos publicados y disponibles por cada marca
        brand_type_products_count = 0
        if product.brand_type_id:
            brand_type_products_count = request.env['product.template'].sudo().search_count([
                ('brand_type_id', '=', product.brand_type_id.id),
                ('id', '!=', product.id),
                ('website_published', '=', True)
            ])
        
        # Obtener qty_available de forma segura usando SUPERUSER_ID
        try:
            product_sudo = request.env['product.template'].sudo().browse(product.id).with_context(
                warehouse=False,
                location=False,
                force_company=request.env.company.id
            )
            qty_available = product_sudo.qty_available
        except Exception as e:
            _logger.info("No se pudo obtener qty_available para producto %s: %s", product.id, e)
            qty_available = None

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
        }
        
        return request.render("theme_xtream.website_view_product_xtream", context)