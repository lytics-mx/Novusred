from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('product_id', 'product_uom_qty', 'discount', 'price_unit')
    def _compute_amount(self):
        for line in self:
            # Verificar si el producto tiene cualquier etiqueta
            if line.product_id.tag_ids:
                price_unit = line.product_id.discount_price
            else:
                price_unit = line.product_id.list_price

            # Calcular el subtotal con el precio correcto
            line.price_subtotal = price_unit * line.product_uom_qty * (1 - (line.discount or 0.0) / 100)
            line.price_tax = line._compute_tax_amount()
            line.price_total = line.price_subtotal + line.price_tax