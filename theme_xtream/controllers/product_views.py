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
        '/view/product/<model("product.template"):product>',
        '/shop/product/<int:product_id>'
    ], type='http', auth="public", website=True, sitemap=False)
    def product_page(self, product=None, product_id=None, **kwargs):
        if product_id:
            product = request.env['product.template'].sudo().browse(product_id)
            if not product.exists():
                return request.not_found()
        
        # Obtener el producto con sudo para evitar problemas de permisos
        product_sudo = product.sudo()
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
        # Obtener la marca del producto actual
        brand_type_products_count = 0
        if product_sudo.brand_type_id:
            brand_type_products_count = request.env['product.template'].sudo().search_count([
                ('brand_type_id', '=', product_sudo.brand_type_id.id),
                ('id', '!=', product_sudo.id),
                ('website_published', '=', True)
            ])
        
        # related_tag_products = []
        # if product.product_tag_ids:
        #     related_tag_products = request.env['product.template'].sudo().search([
        #         ('product_tag_ids', 'in', product.product_tag_ids.ids),
        #         ('id', '!=', product.id),
        #         ('website_published', '=', True)
        #     ], limit=20)

        context = {
            'product': product_sudo,  # <-- Usar product_sudo en lugar de product
            'categories': categories,
            'referer': referer,
            'discounted_price': discounted_price,
            'discount_percentage': discount_percentage,
            'fixed_discount': fixed_discount,
            'list_price': product_sudo.list_price,  # <-- Agrega esto
            'general_images': general_images,
            'brand_type_products_count': brand_type_products_count,
            # 'related_tag_products': related_tag_products,
                 
        }
        return request.render("theme_xtream.website_view_product_xtream", context)