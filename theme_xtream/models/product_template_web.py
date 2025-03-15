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
        'brand.type',
        string='Tipo de Marca',
        help="Selecciona el tipo de marca asociado con este producto."
    )



class BrandType(models.Model):
    _name = 'brand.type'
    _description = 'Tipo de Marca'

    name = fields.Char(
        string='Nombre de la Marca',
        required=True,
        help="Nombre del tipo de marca."
    )
    description = fields.Text(
        string='Descripción',
        help="Descripción del tipo de marca."
    )
    supplier_id = fields.Many2one(
        'res.partner',
        string='Proveedor Asociado',
        help="Proveedor asociado con este tipo de marca."
    )