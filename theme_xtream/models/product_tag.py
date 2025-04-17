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

    start_date = fields.Datetime(
        string="Fecha de inicio",
        help="Fecha y hora en la que la etiqueta comienza a aplicar el descuento."
    )

    end_date = fields.Datetime(
        string="Fecha de fin",
        help="Fecha y hora en la que la etiqueta deja de aplicar el descuento."
    )

    weekend_only = fields.Boolean(
        string="Solo fines de semana",
        help="Si está activado, el descuento solo se aplicará durante los fines de semana."
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
    def _update_discounts(self):
        """Actualiza los descuentos según las fechas y condiciones."""
        current_time = fields.Datetime.now()
        for tag in self.search([]):
            products = self.env['product.template'].search([('product_tag_ids', 'in', tag.id)])
            
            if tag.weekend_only:
                # Verificar si es fin de semana
                if current_time.weekday() in (5, 6):  # 5 = Sábado, 6 = Domingo
                    # Asegurarse de que la etiqueta esté aplicada
                    for product in products:
                        if tag.id not in product.product_tag_ids.ids:
                            product.write({'product_tag_ids': [(4, tag.id)]})  # Agregar la etiqueta
                    tag.discount_percentage = tag.discount_percentage or 0
                else:
                    # Quitar la etiqueta si no es fin de semana
                    for product in products:
                        product.write({'product_tag_ids': [(3, tag.id)]})  # Quitar la etiqueta
                    tag.discount_percentage = 0
            elif tag.start_date and tag.end_date:
                # Verificar si está dentro del rango de fechas
                if tag.start_date <= current_time <= tag.end_date:
                    # Asegurarse de que la etiqueta esté aplicada
                    for product in products:
                        if tag.id not in product.product_tag_ids.ids:
                            product.write({'product_tag_ids': [(4, tag.id)]})  # Agregar la etiqueta
                    tag.discount_percentage = tag.discount_percentage or 0
                else:
                    # Quitar la etiqueta si está fuera del rango de fechas
                    for product in products:
                        product.write({'product_tag_ids': [(3, tag.id)]})  # Quitar la etiqueta
                    tag.discount_percentage = 0
            else:
                # Si no hay condiciones, mantener el descuento actual
                continue
    
            # Actualizar los productos relacionados
            products._compute_discount_percentage_from_tags()
            products._compute_discounted_price()

           