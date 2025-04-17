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

     # Eliminar el campo tag_ids y usar product_tag_ids directamente
     
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
          string="Descuento Fijo",
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

     # additional_images = fields.One2many(
     #      'product.image', 'product_tmpl_id', string="Additional Images"
     # )

     @api.model
     def search(self, args, offset=0, limit=None, order=None, count=False):
          """Modifica la búsqueda para filtrar por proveedores o categorías."""
          # Filtrar por proveedores registrados
          supplier_filter = [('seller_ids', '!=', False)]
          # Filtrar por categorías registradas
          category_filter = [('categ_id', '!=', False)]
          # Combina los filtros con los argumentos existentes
          args = AND([args, OR([supplier_filter, category_filter])])
          return super(ProductTemplate, self).search(args, offset=offset, limit=limit, order=order, count=count)     