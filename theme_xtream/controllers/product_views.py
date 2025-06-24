from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
import logging
_logger = logging.getLogger(__name__)

class ShopController(WebsiteSale):

    @http.route(['/shop/product/<model("product.template"):product>'], type='http', auth="public", website=True, csrf=False)
    def product(self, product, category='', search='', **kwargs):
        """Sobrescribir completamente el método product para evitar errores de permisos"""
        
        if not product or not product.can_access_from_current_website():
            return request.not_found()

        # 🔥 IMPORTANTE: NO llamar a super() para evitar la plantilla base problemática
        
        # Obtener categorías
        categories = []
        categ = product.categ_id
        while categ:
            categories.insert(0, categ)
            categ = categ.parent_id

        # Obtener referer
        referer = request.httprequest.headers.get('Referer')
        if not referer or referer == request.httprequest.url:
            referer = '/shop'
            
        # Cálculos de precio
        list_price = product.list_price if product.list_price is not None else 0
        discounted_price = list_price
        if hasattr(product, 'discounted_price') and product.discounted_price is not None:
            discounted_price = product.discounted_price

        fixed_discount = 0
        discount_percentage = 0
        if list_price > discounted_price:
            fixed_discount = list_price - discounted_price
            discount_percentage = int(100 * fixed_discount / list_price)
        
        # Obtener imágenes
        general_images = request.env['banner.image.line'].search([
            ('name', '=', 'metodos de pago'),
            ('is_active_carousel', '=', True)
        ])    

        # Contar productos de la marca
        brand_type_products_count = 0
        if product.brand_type_id:
            brand_type_products_count = request.env['product.template'].sudo().search_count([
                ('brand_type_id', '=', product.brand_type_id.id),
                ('id', '!=', product.id),
                ('website_published', '=', True)
            ])

        # ✅ OBTENER STOCK SIN ERRORES
        qty_available = None
        stock_message = "Disponible"
        
        try:
            # Intentar obtener el stock con diferentes métodos
            with request.env.cr.savepoint():
                product_sudo = product.sudo()
                qty_available = product_sudo.qty_available
                stock_message = f"{qty_available} disponibles" if qty_available > 0 else "Agotado"
        except Exception as e:
            _logger.info("Error obteniendo stock con sudo: %s", e)
            try:
                # Método alternativo: usar SQL directo
                request.env.cr.execute("""
                    SELECT COALESCE(SUM(quantity), 0) 
                    FROM stock_quant 
                    WHERE product_id IN (
                        SELECT id FROM product_product WHERE product_tmpl_id = %s
                    )
                """, (product.id,))
                result = request.env.cr.fetchone()
                if result:
                    qty_available = result[0]
                    stock_message = f"{qty_available} disponibles" if qty_available > 0 else "Agotado"
            except Exception as e2:
                _logger.info("Error obteniendo stock con SQL: %s", e2)
                # Último recurso: no mostrar cantidad específica
                qty_available = None
                stock_message = "Disponible"

        # Contexto para la plantilla
        context = {
            'product': product,
            'categories': categories,
            'referer': referer,
            'discounted_price': discounted_price,
            'discount_percentage': discount_percentage,
            'fixed_discount': fixed_discount,
            'list_price': list_price,
            'general_images': general_images,
            'brand_type_products_count': brand_type_products_count,
            'qty_available': qty_available,
            'stock_message': stock_message,
            # Agregar variables que podrían necesitar otras partes del sistema
            'main_object': product,
            'website_sale_order': request.website.sale_get_order(),
        }
        
        # 🎯 USAR TU PLANTILLA PERSONALIZADA (sin herencia problemática)
        return request.render("theme_xtream.website_view_product_xtream", context)

    # Mantener tus rutas personalizadas
    @http.route([
        '/view/<model("product.template"):product>',
        '/view/product/<model("product.template"):product>'
    ], type='http', auth="public", website=True, csrf=False)
    def product_page(self, product, **kwargs):
        # Redirigir a la ruta estándar
        return self.product(product, **kwargs)