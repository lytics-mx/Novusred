from odoo import models, fields, api
from datetime import datetime, timedelta
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
        """Valida las fechas y actualiza el descuento o elimina etiquetas al finalizar el rango."""
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

                # Si el rango de fechas ya pasó, se pone el descuento en 0 y se eliminan las etiquetas
                if end_date_with_tz <= current_datetime:
                    self.discount_percentage = 0
                    products = self.env['product.template'].search([('product_tag_ids', 'in', self.id)])
                    for product in products:
                        product.product_tag_ids = [(3, self.id)]  # Quitar la etiqueta
            except Exception as e:
                _logger.error(f"Error en _onchange_date_range: {e}")

    def _apply_recurrent_discount(self):
        """Aplica o desactiva descuentos según la recurrencia."""
        mexico_tz = pytz.timezone('America/Mexico_City')
        current_datetime = datetime.now(mexico_tz)

        for tag in self.search([('recurrence_type', '!=', 'none')]):
            if tag.recurrence_type == 'weekly':
                # Activar descuento solo los fines de semana
                if current_datetime.weekday() in (5, 6):  # Sábado (5) o Domingo (6)
                    tag.discount_percentage = tag.stored_discount
                else:
                    tag.stored_discount = tag.discount_percentage
                    tag.discount_percentage = 0
            elif tag.recurrence_type == 'biweekly':
                # Activar descuento cada dos semanas
                if (current_datetime - tag.start_date).days % 14 == 0:
                    tag.discount_percentage = tag.stored_discount
                else:
                    tag.stored_discount = tag.discount_percentage
                    tag.discount_percentage = 0
            elif tag.recurrence_type == 'monthly':
                # Activar descuento una vez al mes
                if current_datetime.day == tag.start_date.day:
                    tag.discount_percentage = tag.stored_discount
                else:
                    tag.stored_discount = tag.discount_percentage
                    tag.discount_percentage = 0
    
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

        if 'discount_percentage' in vals or 'is_percentage' in vals:
            for tag in self:
                products = self.env['product.template'].search([('product_tag_ids', 'in', tag.id)])
                products._compute_discount_percentage_from_tags()
                products._compute_discounted_price()
        return res
    
    @api.model
    def create(self, vals):
        """Sincroniza el campo name al crear un product.tag."""
        res = super(ProductTag, self).create(vals)
        if 'name' in vals:
            self.env['website.ribbon'].create({
                'name': vals['name'],
                'bg_color': '#007bff',  # Color de fondo predeterminado
                'text_color': '#ffffff'  # Color de texto predeterminado
            })
        return res

    def writes(self, vals):
        """Sincroniza el campo name al actualizar un product.tag."""
        res = super(ProductTag, self).write(vals)
        if 'name' in vals:
            for tag in self:
                ribbon = self.env['website.ribbon'].search([('name', '=', tag.name)], limit=1)
                if ribbon:
                    ribbon.name = vals['name']
        return res

