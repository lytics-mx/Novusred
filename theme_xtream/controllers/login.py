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
            
            # Enhanced debugging information
            _logger.info("Login attempt for user: %s from IP: %s", login, request.httprequest.remote_addr)
            
            # 1. First check if user exists and is active
            user = request.env['res.users'].sudo().search([
                ('login', '=', login),
                ('active', '=', True)
            ], limit=1)
            
            if not user:
                _logger.warning("Login failed: User %s does not exist or is inactive", login)
                return request.render('theme_xtream.website_login', {
                    'error': _("Invalid credentials"),
                    'redirect': redirect,
                })
            
            # 2. Check if user is a portal user
            if not user.has_group('base.group_portal') or user.has_group('base.group_user'):
                _logger.warning("User %s is not a portal user or has backend access", login)
                return request.render('theme_xtream.website_login', {
                    'error': _("This login is for website users only. Please use the regular login page for administrative access."),
                    'redirect': redirect,
                })
            
            # 3. Try to authenticate
            try:
                db_name = request.session.db or request.env.cr.dbname
                _logger.info("Authenticating against database: %s", db_name)
                
                # Direct authentication method
                user_id = request.env['res.users'].sudo()._login(db_name, login, password)
                
                if user_id:
                    # Create session without using authenticate()
                    request.session.uid = user_id
                    request.session.login = login
                    request.session.session_token = request.env['res.users'].sudo().browse(user_id).session_token
                    request.uid = user_id
                    
                    _logger.info("Authentication successful for user %s (ID: %s)", login, user_id)
                    
                    # Redirect to homepage or requested page
                    return request.redirect(redirect or '/home')
                else:
                    # Authentication returned falsy value
                    _logger.warning("Password validation failed for user %s", login)
                    return request.render('theme_xtream.website_login', {
                        'error': _("Invalid password"),
                        'redirect': redirect,
                    })
                    
            except Exception as e:
                # Log the specific error
                _logger.error("Login error for user %s: %s (Exception type: %s)", 
                             login, str(e), type(e).__name__)
                return request.render('theme_xtream.website_login', {
                    'error': _("System error: {0}".format(str(e)) if request.env.user.has_group('base.group_system') else _("Authentication error")),
                    'redirect': redirect,
                })
        
        return request.render('theme_xtream.website_login', {
            'redirect': redirect,
        })
    
    @http.route(['/shop/signup'], type='http', auth="public", website=True)
    def shop_signup(self, redirect=None, **post):
        """Custom signup page for website users"""
        if request.httprequest.method == 'POST':
            # Check if user already exists
            login = post.get('login')
            if login:
                existing_user = request.env['res.users'].sudo().search([('login', '=', login)], limit=1)
                if existing_user:
                    return request.render('theme_xtream.website_signup', {
                        'error': _("Ya existe una cuenta con este correo electrónico. Por favor utiliza otro correo o recupera tu contraseña."),
                        'redirect': redirect,
                    })
            
            # Create values for user creation
            values = {
                'login': login,
                'name': post.get('name') + ' ' + post.get('last_name', ''),
                'password': post.get('password'),
                'groups_id': [(6, 0, [request.env.ref('base.group_portal').id])],  # Specify portal group directly
            }
            
            try:
                # Create a portal user (no backend access)
                user_sudo = request.env['res.users'].sudo().with_context(
                    no_reset_password=True,
                    signup_valid=True
                ).create(values)
                
                # Log user in - CORRECTED LINE
                db_name = ensure_db()
                request.session.authenticate(db_name, login, values['password'])
                return request.redirect(redirect or '/shop')
            except Exception as e:
                return request.render('theme_xtream.website_signup', {
                    'error': str(e),
                    'redirect': redirect,
                })        
    @http.route(['/shop/reset_password'], type='http', auth="public", website=True)
    def shop_reset_password(self, redirect=None, **post):
        """Custom password reset for website users"""
        if request.httprequest.method == 'POST':
            login = post.get('login')
            if login:
                user = request.env['res.users'].sudo().search([('login', '=', login)])
                if user and user.has_group('base.group_portal'):
                    try:
                        user.action_reset_password()
                        return request.render('theme_xtream.website_reset_password_success', {
                            'message': _("Password reset instructions have been sent to your email.")
                        })
                    except Exception as e:
                        return request.render('theme_xtream.website_reset_password', {
                            'error': str(e),
                            'redirect': redirect,
                        })
                else:
                    return request.render('theme_xtream.website_reset_password', {
                        'error': _("No website account found with this email."),
                        'redirect': redirect,
                    })
        
        return request.render('theme_xtream.website_reset_password', {
            'redirect': redirect,
        })

# Helper function to ensure database
def ensure_db():
    db = request.session.db
    if not db:
        db = request.env.cr.dbname
    if not db:
        raise http.LocalRedirect('/web/database/selector')
    return db