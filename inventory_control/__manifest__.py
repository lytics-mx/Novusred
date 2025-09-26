{
    'name': 'Inventory Control',
    'version': '1.0.0',
    'category': 'Inventory',
    'summary': 'Control de inventario avanzado',
    'description': """
        Módulo de control de productos que incluye:
        - Gestión de tipos de marca
        - Plantillas de productos extendidas
        - Etiquetas de productos
    """,
    'author': 'LyticsMx',
    'website': 'www.lytics.mx',
    'depends': [
        'base',
        'stock',
        'product',
        'sale',
    ],
    'data': [
        # Security
        'security/ir.model.access.csv',
        
        # Views
        'views/brand_type.xml',
        'views/product_template_odoo.xml',
        'views/product_category.xml',
        'views/product_tag.xml',

        #Vista de cotización del módulo CRM
        'views/product_product.xml',
        # 'views/sale_order.xml',
        'views/sale_order_pdf.xml',
        

        
     
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}