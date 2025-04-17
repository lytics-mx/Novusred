from odoo import models, fields, api
from datetime import datetime, timedelta

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

    apply_weekends = fields.Boolean(
        string="Aplicar solo fines de semana",
        help="Si está activado, esta etiqueta aplicará el descuento solo los fines de semana."
    )

    start_date = fields.Datetime(
        string="Fecha de inicio",
        help="Fecha y hora de inicio para aplicar el descuento."
    )

    end_date = fields.Datetime(
        string="Fecha de fin",
        help="Fecha y hora de fin para aplicar el descuento."
    )

    def write(self, vals):
        """Aplica el descuento a los productos relacionados al guardar."""
        res = super(ProductTag, self).write(vals)
        if 'discount_percentage' in vals or 'is_percentage' in vals:
            for tag in self:
                products = self.env['product.template'].search([('product_tag_ids', 'in', tag.id)])
                products._compute_discount_percentage_from_tags()
                products._compute_discounted_price()
        return res

    @api.model
    def _check_expired_discounts(self):
        """Verifica y elimina descuentos expirados."""
        now = datetime.now()
        for tag in self.search([]):
            if tag.apply_weekends:
                # Si es fin de semana, no se hace nada
                if now.weekday() in [5, 6]:  # 5 = Sábado, 6 = Domingo
                    continue
                else:
                    # Si no es fin de semana, restablece el descuento
                    self._reset_discount(tag)
            elif tag.start_date and tag.end_date:
                # Si hay un rango de fechas definido
                if not (tag.start_date <= now <= tag.end_date):
                    self._reset_discount(tag)
            elif tag.end_date and now > tag.end_date:
                # Si solo hay una fecha de fin
                self._reset_discount(tag)

    def _reset_discount(self, tag):
        """Restablece el descuento a 0 en los productos relacionados."""
        products = self.env['product.template'].search([('product_tag_ids', 'in', tag.id)])
        for product in products:
            product.write({'discount_percentage': 0})