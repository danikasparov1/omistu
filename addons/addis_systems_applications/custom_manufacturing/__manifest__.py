# custom_manufacturing/__manifest__.py
{
    'name': 'Custom Manufacturing Module',
    'version': '1.0',
    'summary': 'Add custom fields and menu under Manufacturing',
    'description': 'This module adds a new menu under Manufacturing and allows users to add custom fields.',
    'author': 'Your Name',
    'website': 'https://yourwebsite.com',
    'category': 'Manufacturing',
    'depends': ['mrp'],  # Depends on the Manufacturing module
    'data': [
        'security/ir.model.access.csv',
        'views/custom_manufacturing_views.xml',
    ],
    'installable': True,
    'application': True,
}