{
    'name': 'Payment Request',
    'version': '1.0',
    'category': 'Accounting',
    'summary': 'Module for creating payment requests and reimbursements',
    'depends': ['account', 'hr_expense'],
    'data': [
        'views/payment_request_views.xml',
        'views/payment_request_menus.xml',
        'views/payment_request_report.xml',
        'views/payment_order_wizard_views.xml',
        'security/security.xml', 
        'security/ir.model.access.csv',
     


    ],
    'installable': True,
    'application': False,
}