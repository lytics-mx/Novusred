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

    # ...existing code...
    recurrence_type = fields.Selection(
            [('none', 'Sin recurrencia'),
             ('weekly', 'Semanal'),
             ('biweekly', 'Quincenal'),
             ('monthly', 'Mensual')],
            string="Recurrencia",
            default='none',
            help="Define si el descuento se aplica de forma recurrente."
        )
    
    # Campos adicionales para recurrencia avanzada
    recurrence_day = fields.Selection(
        [('0', 'Lunes'), ('1', 'Martes'), ('2', 'Miércoles'), 
         ('3', 'Jueves'), ('4', 'Viernes'), ('5', 'Sábado'), ('6', 'Domingo')],
        string="Día de la semana",
        help="Día de la semana para aplicar el descuento recurrente (solo para recurrencia semanal)."
    )
    
    recurrence_day_month = fields.Integer(
        string="Día del mes",
        default=1,
        help="Día del mes para aplicar el descuento (solo para recurrencia mensual y quincenal)."
    )
    
    recurrence_duration = fields.Integer(
        string="Duración (días)",
        default=1,
        help="Duración en días que se aplica el descuento en cada recurrencia."
    )
    
    preserve_products = fields.Boolean(
        string="Mantener productos",
        default=False,
        help="Si está activado, no eliminará los productos relacionados cuando expire el descuento."
    )
    
    is_active = fields.Boolean(
        string="Activo",
        default=True,
        help="Indica si el descuento está activo."
    )
    
    # ...existing code...

    flash_hours = fields.Integer(
        string="Horas de relámpago",
        default=1,
        help="Duración en horas para la oferta relámpago (máximo 6 horas)."
    )

    stored_discount = fields.Float(
        string="Descuento almacenado",
        help="Almacena el valor del descuento para activarlo nuevamente según la recurrencia."
    )


    # ...existing code...
    def sync_discount(self):
        """
        Botón para sincronizar el descuento:
        - Si está activo, aplica el descuento a los productos relacionados
        - Si no está activo, quita el descuento pero mantiene los productos relacionados
        """
        for tag in self:
            products = self.env['product.template'].search([('product_tag_ids', 'in', tag.id)])
            
            if tag.is_active:
                # Activar descuento
                if tag.stored_discount > 0:
                    tag.discount_percentage = tag.stored_discount
                # Asegurar que los productos tengan la etiqueta visible en el sitio web
                for product in products:
                    if product.website_published:
                        product.is_discount_tag_visible = True
            else:
                # Desactivar descuento pero mantener productos
                tag.stored_discount = tag.discount_percentage
                tag.discount_percentage = 0
                # Hacer que la etiqueta no sea visible en el sitio web
                for product in products:
                    product.is_discount_tag_visible = False
                    
            # Recalcular precios con descuento
            products._compute_discount_percentage_from_tags()
            products._compute_discounted_price()
            
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
    # ...existing code...


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

    # ...existing code...
    def _apply_recurrent_discount(self):
        """Aplica o desactiva descuentos según la recurrencia avanzada."""
        mexico_tz = pytz.timezone('America/Mexico_City')
        current_datetime = datetime.now(mexico_tz)
        today = current_datetime.date()
    
        for tag in self.search([('recurrence_type', '!=', 'none')]):
            # Verificar si debe activarse según el tipo de recurrencia
            should_activate = False
            
            if tag.recurrence_type == 'weekly' and tag.recurrence_day:
                # Activar descuento en el día de la semana específico
                if current_datetime.weekday() == int(tag.recurrence_day):
                    should_activate = True
                    
            elif tag.recurrence_type == 'biweekly' and tag.recurrence_day_month:
                # Activar descuento en el día específico y también 15 días después
                day = tag.recurrence_day_month
                if today.day == day or today.day == (day + 15) % 30 or (day > 28 and today.day == today.replace(day=28).day):
                    should_activate = True
                    
            elif tag.recurrence_type == 'monthly' and tag.recurrence_day_month:
                # Activar descuento en el día específico del mes
                if today.day == tag.recurrence_day_month:
                    should_activate = True
            
            # Si debe activarse, creamos un rango de fechas basado en la duración
            if should_activate:
                tag.is_active = True
                tag.discount_percentage = tag.stored_discount
                
                # Actualizamos las fechas de inicio y fin
                start_date = current_datetime.replace(tzinfo=None)
                end_date = start_date + timedelta(days=tag.recurrence_duration)
                tag.start_date = start_date
                tag.end_date = end_date
                
                # Aplicar a los productos relacionados
                products = self.env['product.template'].search([('product_tag_ids', 'in', tag.id)])
                for product in products:
                    if product.website_published:
                        product.is_discount_tag_visible = True
                
                products._compute_discount_percentage_from_tags()
                products._compute_discounted_price()
            
            # Si ya pasó el período de descuento, lo desactivamos
            elif tag.end_date and tag.end_date < fields.Datetime.now():
                if tag.is_active:
                    tag.is_active = False
                    tag.stored_discount = tag.discount_percentage
                    tag.discount_percentage = 0
                    
                    # Hacer que la etiqueta no sea visible en el sitio web
                    products = self.env['product.template'].search([('product_tag_ids', 'in', tag.id)])
                    for product in products:
                        product.is_discount_tag_visible = False
    # ...existing code...

    # ...existing code...
    def write(self, vals):
        """Aplica el descuento a los productos relacionados y maneja etiquetas expiradas."""
        res = super(ProductTag, self).write(vals)
        
        if 'end_date' in vals or 'is_active' in vals:
            for tag in self:
                if (tag.end_date and tag.end_date <= fields.Datetime.now()) or not tag.is_active:
                    # Buscar productos relacionados con esta etiqueta
                    products = self.env['product.template'].search([('product_tag_ids', 'in', tag.id)])
                    
                    if not tag.preserve_products:
                        # Eliminar la etiqueta de los productos si no se deben preservar
                        for product in products:
                            product.write({'product_tag_ids': [(3, tag.id)]})
                    else:
                        # Solo hacer invisible la etiqueta en el sitio web
                        for product in products:
                            product.is_discount_tag_visible = False
                            
        if 'discount_percentage' in vals or 'is_percentage' in vals:
            for tag in self:
                products = self.env['product.template'].search([('product_tag_ids', 'in', tag.id)])
                products._compute_discount_percentage_from_tags()
                products._compute_discounted_price()
                
        return res
    # ...existing code...


    # ...existing code...
    @api.model
    def remove_expired_tags(self):
        """Elimina o desactiva etiquetas expiradas según la configuración."""
        now = fields.Datetime.now()
        expired_tags = self.search([('end_date', '<=', now), ('is_active', '=', True)])
        
        for tag in expired_tags:
            # Guardar el valor del descuento para futuras recurrencias
            tag.stored_discount = tag.discount_percentage
            tag.discount_percentage = 0
            tag.is_active = False
            
            # Buscar productos relacionados con esta etiqueta
            products = self.env['product.template'].search([('product_tag_ids', 'in', tag.id)])
            
            if not tag.preserve_products:
                # Eliminar la etiqueta de los productos si no se deben preservar
                for product in products:
                    product.write({'product_tag_ids': [(3, tag.id)]})
            else:
                # Solo hacer invisible la etiqueta en el sitio web
                for product in products:
                    product.is_discount_tag_visible = False
    # ...existing code...