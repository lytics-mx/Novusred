from odoo import models, fields, api
from datetime import datetime  # Importar datetime


class ProductTemplate(models.Model):
     _inherit = 'product.template'
#Elimninar el campo de la marca el de brand_id     
     brand_ids = fields.Many2many(
          'product.brand',
          'product_template_brand_rel',  # Relación con las marcas
          'product_id',  # Relación al producto
          'brand_id',  # Relación con la marca
          string='Marcas',
          help="Selecciona o registra marcas asociadas con este producto."
     )

     technical_document_ids = fields.Many2many(
          'ir.attachment',
          'product_template_document_rel',  # Relación con los documentos
          'product_id',  # Relación al producto
          'attachment_id',  # Relación con el archivo
          string='Documentos técnicos',
          domain=[('mimetype', 'not ilike', 'image/')],  # Excluye imágenes
          help="Sube documentos técnicos o fichas técnicas para este producto."
     )
     
     brand_type_id = fields.Many2one(
          comodel_name='brand.type',
          string='Marca',
          help='Select the brand type for this product'
     )
    
     discount_percentage = fields.Float(
          string="Descuento (%)",
          compute="_compute_discount_percentage_from_tags",
          store=True,
          help="Porcentaje de descuento aplicado al producto."
     )

     discounted_price = fields.Float(
          string="Precio con Descuento",
          compute="_compute_discounted_price",
          store=True,
          help="Precio del producto después de aplicar el descuento."
     )

     free_shipping = fields.Boolean('Envío Gratis', default=False, tracking=True)

     is_discount_tag_visible = fields.Boolean(
          string="Etiqueta de descuento visible",
          default=True,
          help="Controla si la etiqueta de descuento es visible en el sitio web"
     )
        
     @api.model
     def update_free_shipping_from_model(self):
          """Actualiza el campo free_shipping basado en el modelo free.shipping"""
          shipping_model = self.env['free.shipping'].sudo().search([], limit=1)
          if shipping_model and shipping_model.product_ids:
               # Resetear todos los free_shipping a False primero
               self.sudo().search([]).write({'free_shipping': False})
               
               # Marcar solo los productos relacionados
               shipping_model.product_ids.write({'free_shipping': True})


     @api.depends('product_tag_ids.discount_percentage', 'product_tag_ids.is_percentage')
     def _compute_discount_percentage_from_tags(self):
          """Calcula el descuento basado en las etiquetas asignadas."""
          for product in self:
               if product.product_tag_ids:
                    percentage_discounts = [
                         tag.discount_percentage for tag in product.product_tag_ids if tag.is_percentage
                    ]
                    fixed_discounts = [
                         tag.discount_percentage for tag in product.product_tag_ids if not tag.is_percentage
                    ]
                    # Toma el mayor porcentaje si hay descuentos porcentuales
                    product.discount_percentage = max(percentage_discounts) if percentage_discounts else 0
                    # Suma los descuentos fijos
                    product.fixed_discount = sum(fixed_discounts)
               else:
                    product.discount_percentage = 0
                    product.fixed_discount = 0

     @api.depends('list_price', 'discount_percentage', 'fixed_discount')
     def _compute_discounted_price(self):
          """Calcula el precio ajustado basado en el descuento."""
          for product in self:
               price = product.list_price
               if product.discount_percentage > 0:
                    price *= (1 - (product.discount_percentage / 100))
               if product.fixed_discount > 0:
                    price -= product.fixed_discount
               product.discounted_price = max(price, 0)  # Evita precios negativos

     fixed_discount = fields.Float(
          string="Monto Fijo",
          compute="_compute_discount_percentage_from_tags",
          store=True,
          help="Cantidad fija de descuento aplicada al producto."
     )

     @api.depends('brand_type_id')
     def _compute_brand_website(self):
          for product in self:
               product.brand_website = product.brand_type_id.name if product.brand_type_id else ''

     brand_website = fields.Char(
          string='Marca en el sitio web',
          compute='_compute_brand_website',
          store=True,
          help='Displays the brand type on the website'
     )

     @api.depends('public_categ_ids')
     def _compute_categ_id(self):
         """Sincroniza categ_id con public_categ_ids."""
         for product in self:
             product.categ_id = product.public_categ_ids[:1].id if product.public_categ_ids else False


     offer_end_time = fields.Datetime(
          string="Fecha de fin de la oferta",
          compute="_compute_offer_end_time",
          store=True,
          help="Fecha y hora en que termina la oferta más cercana para este producto."
     )

     @api.depends('product_tag_ids.end_date')
     def _compute_offer_end_time(self):
          """Calcula la fecha de fin de la oferta basada en las etiquetas relacionadas."""
          for product in self:
               # Obtén todas las fechas de fin de las etiquetas relacionadas
               end_dates = product.product_tag_ids.mapped('end_date')
               # Selecciona la fecha más cercana (si hay varias etiquetas)
               product.offer_end_time = min(end_dates) if end_dates else False

     def get_time_remaining(self):
         """Calcula el tiempo restante para la fecha de finalización."""
         time_remaining = {}
         for product in self:
             # Verifica si hay etiquetas con una fecha de finalización válida
             if product.product_tag_ids and product.product_tag_ids[0].end_date:
                 end_date = fields.Datetime.from_string(product.product_tag_ids[0].end_date)
                 now = datetime.now()
                 delta = end_date - now
                 if delta.total_seconds() > 0:
                     # Si la oferta aún está activa, calcula el tiempo restante
                     days = delta.days
                     hours, remainder = divmod(delta.seconds, 3600)
                     minutes, _ = divmod(remainder, 60)
                     time_remaining[product.id] = f"{days}d {hours}h {minutes}m"
                 else:
                     # Si la oferta ya terminó, muestra "¡Finalizado!"
                     time_remaining[product.id] = "¡Finalizado!"
             else:
                 # Si no hay fecha de finalización, muestra "Sin fecha"
                 time_remaining[product.id] = "Sin fecha"
         return time_remaining