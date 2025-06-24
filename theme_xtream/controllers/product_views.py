from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
import logging
_logger = logging.getLogger(__name__)

class ShopController(WebsiteSale):

    @http.route([
        '/shop/product/<model("product.template"):product>',
        '/view/<model("product.template"):product>',
        '/view/product/<model("product.template"):product>'
    ], type='http', auth="public", website=True, csrf=False)

    def product_page(self, product, **kwargs):
        if not product:
            return request.not_found()
            
        # Obtener datos sin usar campos de inventario
        categories = []
        categ = product.categ_id
        while categ:
            categories.insert(0, categ)
            categ = categ.parent_id

        referer = request.httprequest.headers.get('Referer')
        if not referer or referer == request.httprequest.url:
            referer = '/subcategory'
            
        # Cálculos de precio sin problemas de permisos
        list_price = product.list_price if product.list_price is not None else 0
        discounted_price = list_price
        if hasattr(product, 'discounted_price') and product.discounted_price is not None:
            discounted_price = product.discounted_price

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
        if product.brand_type_id:
            brand_type_products_count = request.env['product.template'].sudo().search_count([
                ('brand_type_id', '=', product.brand_type_id.id),
                ('id', '!=', product.id),
                ('website_published', '=', True)
            ])

        # ✅ OBTENER STOCK DE FORMA SEGURA
        try:
            # Usar sudo() para obtener el stock sin problemas de permisos
            product_sudo = product.sudo()
            qty_available = product_sudo.qty_available
            stock_message = f"{qty_available} disponibles" if qty_available > 0 else "Agotado"
        except Exception as e:
            _logger.warning("Error obteniendo stock: %s", e)
            qty_available = None
            stock_message = "Disponible"

        context = {
            'product': product,
            'categories': categories,
            'referer': referer,
            'discounted_price': discounted_price,
            'discount_percentage': discount_percentage,
            'fixed_discount': fixed_discount,
            'list_price': product.list_price,
            'general_images': general_images,
            'brand_type_products_count': brand_type_products_count,
            'qty_available': qty_available,  # ✅ Pasar el stock al contexto
            'stock_message': stock_message,  # ✅ Mensaje preparado
        }
        
        return request.render("theme_xtream.website_view_product_xtream", context)