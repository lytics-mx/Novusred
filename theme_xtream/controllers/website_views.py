from odoo import http
from odoo.http import request

class WebsiteShop(http.Controller):

    @http.route(['/shop/product/<model("product.template"):product>'], type='http', auth='public', website=True)
    def product_page(self, product, **kwargs):
        """
        Renderiza la página del producto y guarda los productos visitados en la sesión.
        """
        # Recuperar la lista de productos vistos de la sesión
        viewed_products = request.session.get('viewed_products', [])
        
        # Agregar el producto actual si no está ya en la lista
        if product.id not in viewed_products:
            viewed_products.append(product.id)
        
        # Limitar la lista a los últimos 10 productos vistos
        viewed_products = viewed_products[-10:]
        
        # Guardar la lista actualizada en la sesión
        request.session['viewed_products'] = viewed_products

        # Renderizar la página del producto
        return request.render('theme_xtream.product_page_template', {
            'product': product,
        })