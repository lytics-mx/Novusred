import requests
from odoo import http
from odoo.http import request

class MiSitioWeb(http.Controller):
    @http.route('/home', type='http', auth='public', website=True)
    def mi_pagina(self, **kw):
        # Hacer una solicitud HTTP al otro sitio web
        response = requests.get('http://novured-desarrollo.lytics.mx:8070/es')
        
        # Verificar si la solicitud fue exitosa
        if response.status_code == 200:
            contenido = response.text
        else:
            contenido = "No se pudo obtener la información del sitio web."

        # Renderizar la plantilla con el contenido obtenido
        return request.render('portal_web_lytics.lytics_template', {
            'contenido': contenido
        })