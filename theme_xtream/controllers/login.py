from odoo import http, fields, _
from odoo.http import request
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.exceptions import UserError


class WebsiteAuth(http.Controller):
    @http.route(['/shop/login'], type='http', auth="public", website=True)
    def shop_login(self, redirect=None, **post):
        """Custom login page for website users"""
        if request.httprequest.method == 'POST':
            ensure_db()
            
            # Get login credentials
            login = post.get('login', '')
            password = post.get('password', '')
            
            # Try to authenticate
            try:
                uid = request.session.authenticate(request.session.db, login, password)
                if uid:
                    user = request.env['res.users'].sudo().browse(uid)
                    # Check if user is a website user only (no backend access)
                    if user.has_group('base.group_portal') and not user.has_group('base.group_user'):
                        # Redirect to homepage or requested page
                        return request.redirect(redirect or '/shop')
                    else:
                        # If user has backend access, log them out to prevent access
                        request.session.logout()
                        return request.render('theme_xtream.website_login', {
                            'error': _("This login is for website users only. Please use the regular login page for administrative access."),
                            'redirect': redirect,
                        })
            except Exception as e:
                return request.render('theme_xtream.website_login', {
                    'error': _("Wrong login/password"),
                    'redirect': redirect,
                })
        
        return request.render('theme_xtream.website_login', {
            'redirect': redirect,
        })
    
    @http.route(['/shop/signup'], type='http', auth="public", website=True)
    def shop_signup(self, redirect=None, **post):
        """Custom signup page for website users"""
        if request.httprequest.method == 'POST':
            # Create values for user creation
            values = {
                'login': post.get('login'),
                'name': post.get('name') + ' ' + post.get('last_name', ''),
                'password': post.get('password'),
            }
            
            try:
                # Create a portal user (no backend access)
                user_sudo = request.env['res.users'].sudo().with_context(
                    no_reset_password=True,
                    signup_valid=True
                ).create(values)
                
                # Add user to portal group only
                portal_group = request.env.ref('base.group_portal')
                portal_group.sudo().write({'users': [(4, user_sudo.id)]})
                
                # Log user in
                request.session.authenticate(request.session.db, values['login'], values['password'])
                return request.redirect(redirect or '/shop')
            except Exception as e:
                return request.render('theme_xtream.website_signup', {
                    'error': str(e),
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