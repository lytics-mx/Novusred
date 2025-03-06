from odoo import http
from odoo.http import request

class MiSitioWeb(http.Controller):
    @http.route('/es', type='http', auth='public', website=True)
    def mi_pagina(self, **kw):
        return request.render('portal_web_lytics.lytics_template', {})