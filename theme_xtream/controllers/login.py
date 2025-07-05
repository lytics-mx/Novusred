from odoo import http, fields, _
from odoo.http import request
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class WebsiteAuth(http.Controller):
    @http.route(['/shop/login'], type='http', auth="public", website=True)
    def shop_login(self, redirect=None, **post):
        """Custom login page for website users"""
        if request.httprequest.method == 'POST':
            # Get login credentials
            login = post.get('login', '')
            password = post.get('password', '')
            
            _logger.info("Login attempt for user: %s from IP: %s", login, request.httprequest.remote_addr)
            
            # Check if user exists and is active
            user_exists = request.env['res.users'].sudo().search([('login', '=', login)], limit=1)
            if user_exists:
                _logger.info("User found: %s (ID: %s, Active: %s, Groups: %s)", 
                            login, user_exists.id, user_exists.active,
                            ','.join([g.name for g in user_exists.groups_id]))
            else:
                _logger.warning("User not found: %s", login)
            
            # Authentication attempt with detailed error logging
            try:
                uid = request.session.authenticate(request.session.db, login, password)
                if uid:
                    user = request.env['res.users'].sudo().browse(uid)
                    _logger.info("Authentication successful for user %s (ID: %s)", login, uid)
                    return request.redirect(redirect or '/shop')
                else:
                    _logger.warning("Invalid credentials for user %s", login)
                    return request.render('theme_xtream.website_login', {
                        'error': _("Invalid username or password"),
                        'redirect': redirect,
                    })
            except UserError as ue:
                _logger.error("User error during login: %s", str(ue))
                return request.render('theme_xtream.website_login', {
                    'error': str(ue),
                    'redirect': redirect,
                })
            except Exception as e:
                _logger.error("Login error: %s (Exception type: %s)", str(e), type(e).__name__)
                return request.render('theme_xtream.website_login', {
                    'error': _("Authentication error. Please try again."),
                    'redirect': redirect,
                })
        
        return request.render('theme_xtream.website_login', {
            'redirect': redirect,
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
                # Create values for portal user (website-only access)
                name = post.get('name')
                if post.get('last_name'):
                    name += ' ' + post.get('last_name')
                
                # Create a new portal user
                portal_group = request.env.ref('base.group_portal')
                
                # Generate a partner first
                partner_values = {
                    'name': name,
                    'email': login,
                }
                partner = request.env['res.partner'].sudo().create(partner_values)
                
                # Create the user with portal access
                user_values = {
                    'login': login,
                    'name': name,
                    'password': post.get('password'),
                    'partner_id': partner.id,
                    'groups_id': [(6, 0, [portal_group.id])],
                }
                
                user_sudo = request.env['res.users'].sudo().with_context(
                    no_reset_password=True
                ).create(user_values)
                
                _logger.info("Portal user created successfully: %s (ID: %s)", login, user_sudo.id)
                
                # Authenticate the new user
                request.session.authenticate(request.session.db, login, post.get('password'))
                
                return request.redirect(redirect or '/shop')
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