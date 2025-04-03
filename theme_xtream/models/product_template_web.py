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
     
     brand_type_id = fields.Many2many(
          'product.tags',  # Relacionado con product.tags
          string='Marca',
          help='Selecciona las marcas asociadas con este producto.'
     )

     @api.depends('brand_type_id')
     def _compute_brand_website(self):
          for product in self:
               # Concatenar los nombres de las marcas seleccionadas
               product.brand_website = ', '.join(product.brand_type_id.mapped('name')) if product.brand_type_id else ''

     brand_website = fields.Char(
          string='Marca en el sitio web',
          compute='_compute_brand_website',
          store=True,
          help='Muestra las marcas asociadas en el sitio web.'
     )

     # additional_images = fields.One2many(
     #      'product.image', 'product_tmpl_id', string="Additional Images"
     # )