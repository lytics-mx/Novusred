{
    'name': 'Portal Web Lytics',
    'version': '1.0',
    'category': 'Website',
    'depends': ['website'],
    'data': [
        'views/home.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'portal_web_lytics/static/src/css/custom_style.css',
        ],
    },
    'installable': True,
    'application': True,
}
