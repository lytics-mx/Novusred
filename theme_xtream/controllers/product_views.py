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
        '/shop/product/<int:product_id>/<string:product_name>',
        '/view/<model("product.template"):product>',
        '/view/product/<model("product.template"):product>'
    ], type='http', auth="public", website=True, sitemap=False, csrf=False)
    def product_page(self, product_id=None, product_name=None, product=None, **kwargs):
        # Permitir acceso tanto por product_id/product_name como por product (model route)
        if product is None and product_id:
            product_template = request.env['product.template'].sudo().browse(product_id)
        elif product:
            product_template = product.sudo()
        else:
            _logger.warning("No se proporcionó producto válido.")
            return request.not_found()

        if not product_template.exists():
            _logger.warning(f"El producto template con ID {product_id or (product and product.id)} no existe.")
            return request.not_found()

        # Formatear el nombre del producto para comparación
        def format_product_name(name):
            name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('utf-8')
            name = re.sub(r'[^\w\s-]', '', name).strip().replace(' ', '-').lower()
            return name

        # Validar que el nombre en la URL coincida con el nombre real del producto (solo si viene por product_id)
        if product_id and product_name:
            formatted_name = format_product_name(product_template.name)
            if formatted_name != product_name.lower():
                _logger.warning("El nombre del producto en la URL no coincide con el nombre real del producto.")
                return request.not_found()

        product_variant = product_template.product_variant_id
        if not product_variant.exists():
            _logger.warning(f"No se encontró una variante para el producto template con ID {product_template.id}.")
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

        product_sudo = product_template
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