{
    'name': 'Payment Order Management',
    'version': '1.0',
    'category': 'Accounting',
    'summary': 'Manage payment orders and automatically create accounting entries',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/payment_order_form_view.xml',
    ],
    'installable': True,
    'application': False,
}
