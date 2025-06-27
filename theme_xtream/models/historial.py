# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta
import pytz


class Historial(models.Model):
    _name = 'theme_xtream.historial'
    _description = 'Historial de Productos Vistos'

    visitor_id = fields.Many2one('website.visitor', string='Visitante', required=True)
    product_id = fields.Many2one('product.template', string='Producto', required=True)
    visit_datetime = fields.Datetime(string='Fecha de Vista', required=True, default=fields.Datetime.now)

    @api.model
    def create_historial_entry(self, visitor_id, product_id):
        """Crea una entrada en el historial para un visitante y producto."""
        self.create({
            'visitor_id': visitor_id,
            'product_id': product_id,
            'visit_datetime': fields.Datetime.now(),
        })

    @api.model
    def get_grouped_history(self, visitor_id):
        """Obtiene el historial agrupado por períodos."""
        user_tz = self.env.user.tz or 'UTC'
        timezone = pytz.timezone(user_tz)
        now = datetime.now(timezone)
        today = now.date()
        yesterday = today - timedelta(days=1)
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)

        tracks = self.search([('visitor_id', '=', visitor_id)], order='visit_datetime desc')
        grouped_history = {
            'Hoy': [],
            'Ayer': [],
            'Esta semana': [],
            'Este mes': [],
            'Anteriores': []
        }

        for track in tracks:
            visit_date = track.visit_datetime.astimezone(timezone).date()
            if visit_date == today:
                grouped_history['Hoy'].append(track)
            elif visit_date == yesterday:
                grouped_history['Ayer'].append(track)
            elif visit_date >= week_start and visit_date < yesterday:
                grouped_history['Esta semana'].append(track)
            elif visit_date >= month_start and visit_date < week_start:
                grouped_history['Este mes'].append(track)
            else:
                grouped_history['Anteriores'].append(track)

        return grouped_history