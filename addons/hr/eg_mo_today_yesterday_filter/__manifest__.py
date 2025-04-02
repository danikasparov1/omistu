{
    'name': 'Today Yesterday filter in MO',
    'version': '17.1',
    'category': 'mrp',
    'summary': 'This app will display manufacturing order of current day and the previous day order',
    'author': 'INKERP',
    'website': "http://www.inkerp.com",
    'depends': ['mrp'],
    
    'data': [
        'views/manufacturing_order_view.xml',
    ],
    
    'images': ['static/description/banner.gif'],
    'license': "OPL-1",
    'installable': True,
    'application': True,
    'auto_install': False,
}
