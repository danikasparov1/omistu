{
    'name': 'Payment Order Management',
    'version': '1.0',
    'category': 'Accounting',
    'summary': 'Prepare and manage payment order vouchers',
    'author': 'Your Name',
    'depends': ['account', 'base'],
    'data': [
        'security/addis.xml',
        'security/ir.model.access.csv',
        'views/payment_order_menu.xml',
        'views/payment_order_views.xml',
       
    ],
    'installable': True,
    'application': True,
}
