from odoo import models, fields, api
from datetime import datetime, timedelta
import pytz

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
    offer_time_type = fields.Selection([
        ('none', 'Manual'),
        ('day', 'Todo el día'),
        ('flash', 'Relámpago'),
    ], string="Tipo de oferta rápida", default='')

    recurrence_type = fields.Selection(
        [('none', 'Sin recurrencia'),
         ('weekly', 'Semanal'),
         ('biweekly', 'Quincenal'),
         ('monthly', 'Mensual')],
        string="Recurrencia",
        default='none',
        help="Define si el descuento se aplica de forma recurrente."
    )

    flash_hours = fields.Integer(
        string="Horas de relámpago",
        default=1,
        help="Duración en horas para la oferta relámpago (máximo 6 horas)."
    )

    retain_products = fields.Boolean(
        string="Retener productos",
        default=False,
        help="Si está activado, los productos no perderán esta etiqueta al expirar el plazo, pero se ocultarán en el e-commerce."
    )
    def toggle_retain_products(self):
        """Botón para activar/desactivar la retención de productos al expirar la etiqueta."""
        for tag in self:
            tag.retain_products = not tag.retain_products
            # Si se activa la retención y hay un descuento, guardarlo
            if tag.retain_products and tag.discount_percentage:
                tag.stored_discount = tag.discount_percentage




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



    @api.onchange('offer_time_type', 'flash_hours')
    def _onchange_offer_time_type(self):
        if self.offer_time_type == 'none':
            self.start_date = False
            self.end_date = False
            return
        mexico_tz = pytz.timezone('America/Mexico_City')
        now = datetime.now(mexico_tz).replace(minute=0, second=0, microsecond=0)
        naive_now = now.replace(tzinfo=None)
        if self.offer_time_type == 'day':
            self.start_date = naive_now
            self.end_date = naive_now + timedelta(hours=24)
        elif self.offer_time_type == 'flash' and self.flash_hours:
            self.start_date = naive_now
            self.end_date = naive_now + timedelta(hours=self.flash_hours)

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

    def write(self, vals):
        """Aplica el descuento a los productos relacionados y maneja etiquetas expiradas."""
        res = super(ProductTag, self).write(vals)
        if 'end_date' in vals:
            for tag in self:
                if tag.end_date and tag.end_date <= fields.Datetime.now():
                    # Buscar productos relacionados con esta etiqueta
                    products = self.env['product.template'].search([('product_tag_ids', 'in', tag.id)])
                    for product in products:
                        if not tag.retain_products:
                            product.write({'product_tag_ids': [(3, tag.id)]})  # Eliminar la etiqueta
                        else:
                            # Ocultar el producto en el e-commerce pero mantener la etiqueta
                            product.write({'website_published': False})
                            # Guardar el descuento actual y ponerlo a cero
                            if tag.discount_percentage:
                                tag.stored_discount = tag.discount_percentage
                                tag.discount_percentage = 0
        if 'discount_percentage' in vals or 'is_percentage' in vals:
            for tag in self:
                products = self.env['product.template'].search([('product_tag_ids', 'in', tag.id)])
                products._compute_discount_percentage_from_tags()
                products._compute_discounted_price()
        return res


    @api.model
    def remove_expired_tags(self):
        """Maneja etiquetas expiradas según la configuración de retención."""
        now = fields.Datetime.now()
        expired_tags = self.search([('end_date', '<=', now)])
        for tag in expired_tags:
            # Buscar productos relacionados con esta etiqueta
            products = self.env['product.template'].search([('product_tag_ids', 'in', tag.id)])
            for product in products:
                if not tag.retain_products:
                    product.write({'product_tag_ids': [(3, tag.id)]})  # Eliminar la etiqueta
                else:
                    # Ocultar el producto en el e-commerce pero mantener la etiqueta
                    product.write({'website_published': False})
                    # Guardar el descuento actual y ponerlo a cero si hay descuento
                    if tag.discount_percentage:
                        tag.stored_discount = tag.discount_percentage
                        tag.discount_percentage = 0

    def reactivate_discount(self):
        """Botón para reactivar el descuento guardado y hacer visibles los productos."""
        for tag in self:
            if tag.retain_products and tag.stored_discount:
                tag.discount_percentage = tag.stored_discount
                # Buscar productos relacionados con esta etiqueta
                products = self.env['product.template'].search([('product_tag_ids', 'in', tag.id)])
                for product in products:
                    product.write({'website_published': True})
                # Establecer nuevas fechas de inicio y fin
                mexico_tz = pytz.timezone('America/Mexico_City')
                now = datetime.now(mexico_tz).replace(tzinfo=None)
                tag.start_date = now
                tag.end_date = now + timedelta(days=7)  # Por defecto una semana