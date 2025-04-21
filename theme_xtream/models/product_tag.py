from odoo import models, fields, api
from datetime import datetime
import pytz
import logging

_logger = logging.getLogger(__name__)


class ProductTag(models.Model):
    _inherit = 'product.tag'

    discount_percentage = fields.Float(
        string="Descuento",
        help="Porcentaje o cantidad de descuento aplicado a los productos con esta etiqueta."
    )

    is_percentage = fields.Boolean(
        string="¿Es porcentaje?",
        default=True,
        help="Si está activado, el descuento se interpreta como un porcentaje. Si no, como una cantidad fija."
    )

    start_date = fields.Datetime(
        string="Fecha de inicio",
        help="Seleccione la fecha de inicio para aplicar el descuento."
    )

    end_date = fields.Datetime(
        string="Fecha de fin",
        help="Seleccione la fecha de fin para aplicar el descuento."
    )

    recurrence_type = fields.Selection(
        [('none', 'Sin recurrencia'),
         ('weekly', 'Semanal'),
         ('biweekly', 'Quincenal'),
         ('monthly', 'Mensual')],
        string="Recurrencia",
        default='none',
        help="Define si el descuento se aplica de forma recurrente."
    )

    stored_discount = fields.Float(
        string="Descuento almacenado",
        help="Almacena el valor del descuento para activarlo nuevamente según la recurrencia."
    )

    @api.onchange('start_date', 'end_date')
    def _onchange_date_range(self):
        """Valida las fechas y muestra advertencias si son incorrectas."""
        if self.start_date and self.end_date:
            try:
                # Configuramos la zona horaria de México
                mexico_tz = pytz.timezone('America/Mexico_City')
                current_datetime = datetime.now(mexico_tz)

                # Convertimos las fechas a la misma zona horaria
                start_date_with_tz = pytz.utc.localize(self.start_date).astimezone(mexico_tz)
                end_date_with_tz = pytz.utc.localize(self.end_date).astimezone(mexico_tz)

                # Validamos que la fecha de inicio sea menor o igual a la fecha de fin
                if start_date_with_tz > end_date_with_tz:
                    self.start_date = False
                    self.end_date = False
                    return {
                        'warning': {
                            'title': "Error en el rango de fechas",
                            'message': "La fecha de inicio no puede ser mayor que la fecha de fin.",
                        }
                    }

                # Si la fecha de fin ya pasó, muestra una advertencia
                if end_date_with_tz <= current_datetime:
                    return {
                        'warning': {
                            'title': "Fecha de fin pasada",
                            'message': "La fecha de fin ya ha pasado. Por favor, seleccione una fecha futura.",
                        }
                    }
            except Exception as e:
                _logger.error(f"Error en _onchange_date_range: {e}")

    def _remove_expired_tags(self):
        """Elimina etiquetas de productos cuando la fecha de fin ha pasado."""
        mexico_tz = pytz.timezone('America/Mexico_City')
        current_datetime = datetime.now(mexico_tz)

        # Buscar etiquetas cuya fecha de fin ya haya pasado
        expired_tags = self.search([('end_date', '<=', current_datetime)])
        _logger.info(f"Etiquetas expiradas encontradas: {expired_tags}")

        for tag in expired_tags:
            # Poner el descuento en 0
            tag.discount_percentage = 0
            _logger.info(f"Procesando etiqueta: {tag.name}")

            # Buscar productos relacionados con la etiqueta
            products = self.env['product.template'].search([('product_tag_ids', 'in', tag.id)])
            _logger.info(f"Productos relacionados encontrados: {products}")

            # Eliminar la etiqueta de los productos relacionados
            for product in products:
                product.write({'product_tag_ids': [(3, tag.id)]})
                _logger.info(f"Etiqueta {tag.id} eliminada del producto {product.name}")

            # Confirmar que la etiqueta fue eliminada
            _logger.info(f"Etiqueta {tag.id} procesada y eliminada de los productos relacionados.")

    def write(self, vals):
        """Aplica el descuento a los productos relacionados al guardar y elimina etiquetas expiradas."""
        res = super(ProductTag, self).write(vals)

        # Verificar si las fechas de fin han pasado y eliminar etiquetas expiradas
        self._remove_expired_tags()

        return res