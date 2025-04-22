{
    'name': 'Car Weight Tracking for Manufacturing',
    'version': '17.0.1.0.0',
    'summary': 'Tracks car entry and exit weights to calculate soap product weight.',
    'category': 'Manufacturing',
    'author': 'Daniel Tibebu',
    'depends': ['mrp'],
    'data': [
        'security/ir.model.access.csv',
        'views/car_weight_views.xml',
        'views/car_registration.xml',
    ],
    'installable': True,
    'application': False,
}
