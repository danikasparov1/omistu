{
    'name': 'MRP Customization - Other Fields',
    'version': '1.0',
    'summary': 'Adds an "Other Fields" notebook to Manufacturing Configuration settings.',
    'author': 'Daniel Tibebu',
    'website': 'https://addissystem.com',
    'category': 'Manufacturing',
    'license': 'LGPL-3',
    'depends': ['mrp'],
    'data': [
        'views/mrp_config_settings_views.xml',
        'views/mrp_production_report_templates.xml'
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
