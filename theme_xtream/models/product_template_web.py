import http
from httpcore import request
from odoo import models, fields, api




class ProductTemplate(models.Model):
     _inherit = 'product.template'



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

class ProductImage(models.Model):
    _name = 'product.image'
    _description = 'Product Images'

    product_tmpl_id = fields.Many2one(
        comodel_name='product.template',
        string='Product Template',
        required=True
    )
    image = fields.Binary(
        string='Image',
        required=True,
        help='Upload additional images for the product.'
    )
    name = fields.Char(string='Image Name')


class ProductController(http.Controller):

    @http.route(['/product/<model("product.template"):product>'], type='http', auth="public", website=True)
    def product_page(self, product, **kwargs):
        # Obtén las imágenes adicionales del producto
        additional_images = product.product_image_ids
        return request.render('theme_xtream.product_page_template', {
            'product': product,
            'additional_images': additional_images,
        })
