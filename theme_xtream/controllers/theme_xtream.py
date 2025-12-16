# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import http
from odoo.http import request


class WebsiteProduct(http.Controller):
    """ This controller method returns a JSON object that lists
        products newly arrived products.
        :return: a JSON object containing newly arrived products
        :rtype: dict """
    @http.route('/get_arrival_product', auth="public", type='json')
    def get_arrival_product(self):
        """
        This return products based on last created and limits to 6
        """
        return http.Response(template='theme_xtream.new_arrivals_dynamic',
                             qcontext={'product_ids': request.env[
                                 'product.template'].sudo().search(
                                 [('website_published', '=', True)],
                                 order='create_date desc', limit=6)}).render()

    @http.route('/get_testimonials', auth="public", type="json")
    def get_testimonials(self):
        """
        This will return testimonials from backend.
        """
        return http.Response(template='theme_xtream.testimonial',
                             qcontext={'testimonials': request.env[
                                 'xtream.testimonials'].sudo(
                             ).search([])}).render()

    @http.route('/subscribe_newsletter', auth='public', type='json')
    def subscribe_newsletter(self, **kw):
        """
        To save email to newsletter mail list
        """
        if request.env['mailing.contact'].sudo().search([
            ("email", "=", kw.get("email")),
            ("list_ids", "in", [
                request.env.ref('mass_mailing.mailing_list_data').id])]):
            return False
        if request.env.user._is_public():
            visitor_sudo = (request.env['website.visitor'].sudo()
                            ._get_visitor_from_request())

            name = visitor_sudo.display_name if visitor_sudo else "Website Visitor"
        else:
            name = request.env.user.partner_id.name
        request.env['mailing.contact'].sudo().create({
            "name": name,
            "email": kw.get('email'),
            "list_ids": [request.env.ref('mass_mailing.mailing_list_data').id]
        })
        return True
    

    def _get_product_template(self, product_id):
        """Sobrescribe el método para registrar el producto visto."""
        product = super(WebsiteProduct, self)._get_product_template(product_id)
        if request.env.user.id:
            request.env['product.view.history'].sudo().add_product_to_history(product.id)
        return product


    @http.route('/about', auth='public', website=True)
    def about(self, **kw):
        return http.request.render('theme_xtream.xtream_about')
        
    @http.route('/terms', auth='public', website=True)
    def policies(self, **kw):
        return http.request.render('theme_xtream.terms_and_conditions')

    @http.route('/purchasing_policies', auth='public', website=True)
    def purchasing_policies(self, **kw):
        return http.request.render('theme_xtream.purchasing_policies')
    
    @http.route('/warranty_policies', auth='public', website=True)
    def warranty_policies(self, **kw):
        return http.request.render('theme_xtream.warranty_policies')    
    
    @http.route('/delivery_policies', auth='public', website=True)
    def delivery_policies(self, **kw):
        return http.request.render('theme_xtream.delivery_policies')
    
    @http.route('/privacy_policy', auth='public', website=True)
    def privacy_policy(self, **kw):
        return http.request.render('theme_xtream.privacy_policy')
    
    @http.route('/refund_policies', auth='public', website=True)
    def refund_policies(self, **kw):
        return http.request.render('theme_xtream.refund_policies')
    
    @http.route('/payment_policies', auth='public', website=True)
    def payment_policies(self, **kw):
        return http.request.render('theme_xtream.payment_policies')
    
    
    @http.route('/descubre', auth='public', website=True)
    def descubre(self, **kw):
        """
        Renderiza la página Descubre con categorías destacadas.
        """
        return http.request.render('theme_xtream.descubre')

    @http.route('/', auth='public', website=True)
    def home(self, **kw):
        """
        Renderiza la página de inicio con el nuevo template.
        """
        return http.request.render('theme_xtream.xtream_inicio_web')


