from odoo import http, fields, _
from odoo.http import request
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.web.controllers.home import Home
from odoo.exceptions import UserError
import logging


_logger = logging.getLogger(__name__)

class WebsiteAuth(Home):

    @http.route('/web/login', type='http', auth='public', website=True)
    def web_login(self, redirect=None, **kwargs):
        """Override the default login route to handle custom login logic."""
        # Add debug logging
        if not request.env.user._is_public() and request.env.user.has_group('base.group_public'):
            _logger.info("DEBUG: User %s has public group, redirecting to /subcategory", request.env.user.login)
            return request.redirect('/subcategory')
        
        # If this is a POST request (login form submitted)
        if request.httprequest.method == 'POST':
            # Let the parent handle authentication
            response = super(WebsiteAuth, self).web_login(redirect=redirect, **kwargs)
            
            # If login was successful
            if not request.env.user._is_public():
                # Debug logging
                _logger.info("User %s groups: %s", request.env.user.login, 
                            request.env.user.groups_id.mapped('name'))
                
                # Check if the user has the public group
                if request.env.user.has_group('base.group_public'):
                    _logger.info("Redirecting public user %s to /subcategory", request.env.user.login)
                    return request.redirect('/subcategory')
                elif request.env.user.has_group('base.group_user'):
                    return request.redirect('/web')
                elif request.env.user.has_group('base.group_portal'):
                    if request.env.user.has_group('base.group_public'):
                        return request.redirect('/subcategory')
                    return request.redirect('/my')
                else:
                    return request.redirect('/subcategory')
            return response
        
        # GET request handling
        if not request.env.user._is_public():
            if request.env.user.has_group('base.group_public'):
                _logger.info("Redirecting public user %s to /subcategory", request.env.user.login)
                return request.redirect('/subcategory')
            elif request.env.user.has_group('base.group_user'):
                return request.redirect('/web')
            elif request.env.user.has_group('base.group_portal'):
                return request.redirect('/my')
            else:
                return request.redirect('/subcategory')
        
        # Show login form for anonymous users
        return request.render('theme_xtream.website_login', {
            'redirect': redirect or '/subcategory'
        })
    



    @http.route(['/shop/signup'], type='http', auth="public", website=True)
    def shop_signup(self, redirect=None, **post):
        """Custom signup page for website users"""
        if request.httprequest.method == 'POST':
            # Check required fields
            for field in ['login', 'name', 'password']:
                if not post.get(field):
                    return request.render('theme_xtream.website_signup', {
                        'error': _("All fields are required."),
                        'redirect': redirect,
                    })
            
            # Check if user already exists
            login = post.get('login')
            if login:
                existing_user = request.env['res.users'].sudo().search([('login', '=', login)], limit=1)
                if existing_user:
                    return request.render('theme_xtream.website_signup', {
                        'error': _("An account with this email already exists. Please use another email or reset your password."),
                        'redirect': redirect,
                    })
            
            try:
                # Create values for public user
                name = post.get('name')
                if post.get('last_name'):
                    name += ' ' + post.get('last_name')
                
                # Create a new public user
                public_group = request.env.ref('base.group_public')
                
                # Generate a partner first
                partner_values = {
                    'name': name,
                    'email': login,
                }
                partner = request.env['res.partner'].sudo().create(partner_values)
                
                # Create the user with public access
                user_values = {
                    'login': login,
                    'name': name,
                    'password': post.get('password'),
                    'partner_id': partner.id,
                    'groups_id': [(6, 0, [public_group.id])],
                }
                
                user_sudo = request.env['res.users'].sudo().with_context(
                    no_reset_password=True
                ).create(user_values)
                
                _logger.info("Public user created successfully: %s (ID: %s)", login, user_sudo.id)
                
                # Authenticate the new user
                request.session.authenticate(request.session.db, login, post.get('password'))
                
                return request.redirect(redirect or '/subcategory')
            except Exception as e:
                _logger.error("Signup error: %s (Exception type: %s)", str(e), type(e).__name__)
                return request.render('theme_xtream.website_signup', {
                    'error': _("Could not create your account: {0}").format(str(e)),
                    'redirect': redirect,
                })
        
        return request.render('theme_xtream.website_signup', {
            'redirect': redirect,
        })
    
    @http.route(['/shop/reset_password'], type='http', auth="public", website=True)
    def shop_reset_password(self, redirect=None, **post):
        """Custom password reset for website users"""
        if request.httprequest.method == 'POST':
            login = post.get('login')
            if login:
                user = request.env['res.users'].sudo().search([('login', '=', login)])
                if user:
                    try:
                        user.action_reset_password()
                        return request.render('theme_xtream.website_reset_password_success', {
                            'message': _("Password reset instructions have been sent to your email.")
                        })
                    except Exception as e:
                        return request.render('theme_xtream.website_reset_password', {
                            'error': _("Could not reset password: {0}").format(str(e)),
                            'redirect': redirect,
                        })
                else:
                    return request.render('theme_xtream.website_reset_password', {
                        'error': _("No account found with this email."),
                        'redirect': redirect,
                    })
        
        return request.render('theme_xtream.website_reset_password', {
            'redirect': redirect,
        })