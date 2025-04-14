{
    'name': 'MRP Work Order Duration in Hours',
    'version': '17.0.1.0',
    'summary': 'Add expected duration in hours to MRP work orders',
    'author': 'Your Name',
    'category': 'Manufacturing',
    'depends': ['mrp'],
    'data': [
        'security/ir.model.access.csv',
        'views/operation_duration_views.xml',
    ],
    'installable': True,
    'application': False,
}
