from odoo import models, fields, api




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
     is_discounted = fields.Boolean(string="En Oferta", default=False, help="Indica si el producto está en oferta.") 
    
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
     tag_ids = fields.Many2many(
          'product.tag',
          'product_template_tag_rel',  # Nombre de la tabla de relación
          'product_id',  # Campo de relación al producto
          'tag_id',  # Campo de relación a la etiqueta
          string="Etiquetas",
          help="Etiquetas asociadas con este producto."
     )
     @api.depends('list_price', 'discount_percentage')
     def _compute_discounted_price(self):
         """Calcula el precio ajustado basado en el descuento."""
         for product in self:
             if product.discount_percentage > 0:
                 product.discounted_price = product.list_price * (1 - (product.discount_percentage / 100))
             else:
                 product.discounted_price = product.list_price

     @api.depends('tag_ids.discount_percentage')
     def _compute_discount_percentage_from_tags(self):
         """Actualiza el descuento basado en las etiquetas relacionadas."""
         for product in self:
             if product.tag_ids:
                 # Toma el mayor descuento de las etiquetas relacionadas
                 product.discount_percentage = max(product.tag_ids.mapped('discount_percentage'), default=0)
             else:
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