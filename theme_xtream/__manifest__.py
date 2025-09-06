
{
    'name': 'Theme Xtream Fashion',
    'version': '18.0.1.0.0',
    'category': 'Theme/eCommerce',
    'description': 'Design eCommerce Website with Theme Xtream Fashion',
    'summary': 'Theme Xtream Fashion',
    'author': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': "https://www.cybrosys.com",
    'depends': ['product', 'stock', 'base','inventory_control', 'website','website_sale', 'website_sale_wishlist', 'website_mass_mailing'],
    'data': [
        'security/ir.model.access.csv',
        'views/xtream_testimonials_views.xml',
        'views/contact_us_templates.xml',
        'views/footer_templates.xml',
        'views/shop_templates.xml',
        'views/header_templates.xml',
        'views/snippets/snippets_templates.xml',
        'views/snippets/amazing.xml',
        'views/snippets/new_arrivals.xml',
        'views/snippets/discount.xml',
        'views/snippets/main_banner.xml',
        'views/snippets/main_product.xml',
        'views/snippets/testimonial.xml',

# INFORMACIÓN DE POLITICAS        
        'views/policies/about_us_templates.xml',
        'views/policies/terms_and_conditions.xml',
        'views/policies/purchasing_policies.xml',
        'views/policies/warranty_policies.xml',
        'views/policies/delivery_policies.xml',
        'views/policies/privacy_policy.xml',
        'views/policies/refund_policies.xml',
        'views/policies/payment_policies.xml',



# Configuiración del modulo de sitio web en odoo
        'views/website_configuration/imagenes_banner.xml',
        # 'views/website_configuration/free_shipping.xml',

# Vistas de la pagina web
        'views/website_sale/website_history.xml',
        'views/website_sale/website_category.xml',
        'views/website_sale/website_subcategory.xml',
        'views/website_sale/website_brand.xml',
        'views/website_sale/website_view_products.xml',
        'views/website_sale/website_offers.xml',
        'views/website_sale/website_home.xml',
        'views/website_sale/website_login.xml',
        'views/website_sale/website_user_record.xml',
        'views/website_sale/website_whislist.xml',
        'views/website_sale/website_discover.xml',
        'views/website_sale/website_signup_success.xml',




# Búsqueda de productos en la web (incluye marcas y categorías)
        'views/website_sale/search/brand_search.xml',
        'views/website_sale/search/category_search.xml',
        'views/website_sale/search/nav_bar.xml',
        'views/website_sale/search/notificacion.xml',
        


        'views/shop/website_cart.xml',
        'views/shop/website_purchase.xml',
        'views/shop/website_details_purchase.xml',

        'views/csrf_token.xml',






    ],
    'assets': {
      'web.assets_frontend': [
          '/theme_xtream/static/src/css/animate.min.css',
          '/theme_xtream/static/src/css/owl.carousel.min.css',
          '/theme_xtream/static/src/css/owl.theme.default.min.css',
          '/theme_xtream/static/src/css/style.css',
          '/theme_xtream/static/src/css/views_products.css',
          
          '/theme_xtream/static/src/js/owl.carousel.js',
          '/theme_xtream/static/src/js/owl.carousel.min.js',
          '/theme_xtream/static/src/js/new_arrivals.js',
          '/theme_xtream/static/src/js/testimonials.js',
          '/theme_xtream/static/src/js/custom.js',
          '/theme_xtream/static/src/css/custom.css',
          '/theme_xtream/static/src/css/home.css',          
          '/theme_xtream/static/src/css/navbar.css',
          '/theme_xtream/static/src/js/navbar.js',        


      ]
    },
    'images': [
        'static/description/banner.jpg',
        'static/description/theme_screenshot.jpg',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
