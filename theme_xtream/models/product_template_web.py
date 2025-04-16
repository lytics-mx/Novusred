from odoo import models, fields, api

class ProductTemplate(models.Model):
     _inherit = 'product.template'
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
     is_discounted = fields.Boolean(string="En Oferta", default=False, help="Indica si el producto está en oferta.") 
    
     discounted_price = fields.Float(
          string="Precio con Descuento",
          compute="_compute_discounted_price",
          store=True,
          help="Precio del producto después de aplicar el descuento."
     )

     discount_percentage = fields.Float(
          string="Descuento (%)",
          compute="_compute_discount_percentage_from_tags",
          store=True,
          help="Porcentaje de descuento aplicado al producto."
     )

     fixed_discount = fields.Float(
          string="Descuento Fijo",
          compute="_compute_discount_percentage_from_tags",
          store=True,
          help="Descuento fijo aplicado al producto (en pesos)."
     )

     @api.depends('product_tag_ids.discount_value')
     def _compute_discount_percentage_from_tags(self):
          """Calcula el descuento basado en las etiquetas asignadas."""
          for product in self:
               if product.product_tag_ids:
                    # Separar descuentos fijos y porcentuales
                    fixed_discounts = [tag.discount_value for tag in product.product_tag_ids if tag.discount_value >= 1]
                    percentage_discounts = [tag.discount_value for tag in product.product_tag_ids if tag.discount_value < 1]

                    # Aplicar el descuento fijo más alto y el porcentaje más alto
                    product.fixed_discount = max(fixed_discounts, default=0)
                    product.discount_percentage = max(percentage_discounts, default=0) * 100
               else:
                    product.fixed_discount = 0
                    product.discount_percentage = 0




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

     # additional_images = fields.One2many(
     #      'product.image', 'product_tmpl_id', string="Additional Images"
     # )