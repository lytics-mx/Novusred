from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # Sobrescribir el campo price_unit para calcularlo dinámicamente
    price_unit = fields.Float(
        string="Precio unitario",
        compute="_compute_price_unit",
        store=True,
    )

    @api.depends('product_id', 'product_uom_qty', 'discount')
    def _compute_price_unit(self):
        for line in self:
            # Verificar si el producto tiene etiquetas
            if line.product_id.tag_ids:
                # Si tiene etiquetas, usar discounted_price
                line.price_unit = line.product_id.discount_price or line.product_id.list_price
            else:
                # Si no tiene etiquetas, usar list_price
                line.price_unit = line.product_id.list_price

    @api.depends('price_unit', 'product_uom_qty', 'discount')
    def _compute_amount(self):
        for line in self:
            # Calcular el subtotal con el precio unitario correcto
            line.price_subtotal = line.price_unit * line.product_uom_qty * (1 - (line.discount or 0.0) / 100)
            line.price_tax = line._compute_tax_amount()
            line.price_total = line.price_subtotal + line.price_tax