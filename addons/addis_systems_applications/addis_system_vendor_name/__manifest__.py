{
    'name': 'Purchase Vendor Name',
    'version': '1.0',
    'category': 'Purchases',
    'summary': 'Displays vendor name on purchase orders and in reports',
    'description': """
    This module adds the vendor name to the purchase order form and ensures it is displayed prominently in print reports.
    """,
    'website': 'https://addissystem.com',
    'depends': ['purchase','mrp'],
    'data': [
        'views/purchase_order_views.xml',
        'views/report_purchaseorder_templates.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
