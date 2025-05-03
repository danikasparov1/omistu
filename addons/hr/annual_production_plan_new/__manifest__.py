{
    'name': 'Annual Production Plan',
    'version': '1.0',
    'category': 'Manufacturing',
    'summary': 'Manage annual production plans and check production status',
    'description': 'This module allows you to manage annual production plans and check whether they are produced or not.',
    'author': 'Your Name',
    'website': 'https://yourwebsite.com',
    'depends': ['base', 'mrp', 'stock', 'purchase'],
    'data': [
        'security/ir.model.access.csv',
        'views/annual_plan_views.xml',
        'views/menu.xml',
    ],
    
    'installable': True,
    'application': True,
}