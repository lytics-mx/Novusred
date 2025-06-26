from odoo import http
from odoo.http import request

class BannerController(http.Controller):

    @http.route('/banner/images', type='http', auth='public', website=True)
    def get_banner_images(self):
        banners = request.env['banner.image.line'].sudo().search([('is_active_carousel', '=', True), ('name', '=', 'home')], limit=1)
        images = banners.mapped('general_images')
        return request.render('theme_xtream.banner_images_template', {'images': images})