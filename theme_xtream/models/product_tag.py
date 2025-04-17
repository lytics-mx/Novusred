from odoo import models, fields, api
from datetime import datetime
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

    date_range = fields.Datetime(
        string="Rango de fechas",
        help="Seleccione el rango de fechas para aplicar el descuento.",
    )

    weekend_only = fields.Boolean(
        string="Solo fines de semana",
        help="Si está activado, el descuento solo se aplicará durante los fines de semana."
    )

    @api.onchange('date_range')
    def _onchange_date_range(self):
        """Actualiza el descuento a 0 si se selecciona una fecha de fin."""
        if self.date_range:
            # Configuramos la zona horaria de México
            mexico_tz = pytz.timezone('America/Mexico_City')
            current_datetime = datetime.now(mexico_tz)

            # Si la fecha de fin es menor o igual a la actual, se pone el descuento en 0
            if self.date_range and self.date_range <= current_datetime:
                self.discount_percentage = 0

    def write(self, vals):
        """Aplica el descuento a los productos relacionados al guardar."""
        res = super(ProductTag, self).write(vals)
        if 'discount_percentage' in vals or 'is_percentage' in vals:
            for tag in self:
                products = self.env['product.template'].search([('product_tag_ids', 'in', tag.id)])
                products._compute_discount_percentage_from_tags()
                products._compute_discounted_price()
        return res