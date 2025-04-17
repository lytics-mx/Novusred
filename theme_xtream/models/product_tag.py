from odoo import models, fields, api
from datetime import date, datetime, timedelta

class ProductTag(models.Model):
    _inherit = 'product.tag'

    # Campos nuevos
    apply_weekends = fields.Boolean(
        string="Aplicar solo fines de semana",
        help="Si está activado, esta etiqueta solo aplica los fines de semana."
    )
    duration_hours = fields.Integer(
        string="Duración en horas",
        help="Duración en horas después de la cual la etiqueta será eliminada automáticamente."
    )
    start_date = fields.Datetime(
        string="Fecha de inicio",
        help="Fecha y hora de inicio para aplicar esta etiqueta."
    )
    end_date = fields.Datetime(
        string="Fecha de fin",
        help="Fecha y hora de fin para aplicar esta etiqueta."
    )

    @api.model
    def _remove_expired_tags(self):
        """Elimina etiquetas expiradas de los productos."""
        today = datetime.now()
        expired_tags = self.search([
            '|', '|',
            ('expiration_date', '<=', today.date()),
            ('end_date', '<=', today),
            ('duration_hours', '>', 0)
        ])
        for tag in expired_tags:
            if tag.duration_hours > 0:
                creation_time = tag.create_date
                if creation_time + timedelta(hours=tag.duration_hours) <= today:
                    self._remove_tag_from_products(tag)
            elif tag.end_date and tag.end_date <= today:
                self._remove_tag_from_products(tag)
            elif tag.expiration_date and tag.expiration_date <= today.date():
                self._remove_tag_from_products(tag)

    def _remove_tag_from_products(self, tag):
        """Elimina una etiqueta específica de los productos relacionados."""
        products = self.env['product.template'].search([('product_tag_ids', 'in', tag.id)])
        for product in products:
            product.write({'product_tag_ids': [(3, tag.id)]})  # Elimina la etiqueta del producto
            product.write({'discount_percentage': 0})  # Opcional: Reinicia el descuento