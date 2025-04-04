from odoo import http
from odoo.http import request

class WebsiteProduct(http.Controller):
    @http.route('/brand', auth='public', website=True)
    def shop(self, tags=None, **kwargs):
        """
        Filtra los productos según las etiquetas seleccionadas.
        """
        domain = [('website_published', '=', True)]
        if tags:
            tag_ids = [int(tag) for tag in tags.split(',') if tag]
            domain.append(('product_tag_ids', 'in', tag_ids))
        products = request.env['product.template'].sudo().search(domain)
        if request.httprequest.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return request.render('theme_xtream.filtered_product_list', {
                'products': products
            })
        return request.render('theme_xtream.website_brand', {
            'products': products
        })