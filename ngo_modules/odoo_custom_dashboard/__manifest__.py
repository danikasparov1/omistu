# -*- coding: utf-8 -*-
{
    'name' : 'Main Dashboard',
    'version' : '1.0',
    'summary': 'Main Dashboard',
    'sequence': -1,
    'description': """Main Dashboard Custom Dashboard""",
    'category': 'OWL',
    'depends' : ['base', 'web', 'sale', 'board'],
    'data': [
        'views/sales_dashboard.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'assets': {
        'web.assets_backend': [
            'odoo_custom_dashboard/static/src/components/**/*.js',
            'odoo_custom_dashboard/static/src/components/**/*.xml',
            'odoo_custom_dashboard/static/src/components/**/*.scss',
        ],
    },
}
