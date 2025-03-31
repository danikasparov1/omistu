{
    'name': 'Property Management',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Manage properties and integrate with CRM',
    'depends': ['base', 'crm', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'security/group.xml',
        'views/property_view.xml',
        # 'views/crm_menu.xml',
        # 'views/property_menu.xml',
    ],
    'installable': True,
    'auto_install': False,
    'assets': {
    'web.assets_backend': [
        'property_management/static/src/css/property_kanban.css',
    ],
},

}



