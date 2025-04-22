{
    'name': 'Equipment Management',
    'version': '1.0',
    'summary': 'Manage equipment and their components with email notifications.',
    'description': 'Track equipment and components status and get notifications for malfunctioning parts.',
    'category': 'Maintenance',
    'author': 'Your Company',
    'depends': ['base', 'mail', 'stock','mrp'],  # Add stock if necessary
    'data': [
        'views/equipment_view.xml',
        'views/component_view.xml',
        'security/ir.model.access.csv',
        'views/equipment_component_view.xml',
        'views/category.xml',
        'data/equipment_data.xml',
    ],
    'installable': True,
    'application': True,
}
