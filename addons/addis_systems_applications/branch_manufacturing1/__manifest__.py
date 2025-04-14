{
    'name': 'Branch Manufacturing Management',
    'version': '1.0',
    'summary': 'Manage manufacturing orders and operations based on specific branches.',
    'author': 'Your Name',
    'category': 'Manufacturing',
    'depends': ['base', 'mrp'],
    'data': [
        'views/branch_reports_view.xml',
        'views/manufacturing_operation_view.xml',
        # 'views/manufacturing_order_view.xml',
        # 'security/ir.model.access.csv',
        'security/security.xml',
    ],
    'installable': True,
    'application': True,
}
