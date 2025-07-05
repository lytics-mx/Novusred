from odoo import http, fields, _
from odoo.http import request
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class WebsiteAuth(http.Controller):
    @http.route('/web/login', type='http', auth='public', website=True)
    def web_login(self, redirect=None, **kwargs):
        """Override the default login route to handle custom login logic."""
        if request.env.user and request.env.user.id != request.website.user_id.id:
            return request.redirect('/subcategory')
        return AuthSignupHome.web_login(self, redirect=redirect, **kwargs)

    @http.route('/web/logout', type='http', auth='user', website=True)
    def web_logout(self, redirect=None):
        """Override the default logout route to handle custom logout logic."""
        if request.env.user and request.env.user.id != request.website.user_id.id:
            return request.redirect('/subcategory')
        return AuthSignupHome.web_logout(self, redirect=redirect)