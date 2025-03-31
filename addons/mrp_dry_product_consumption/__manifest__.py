 # __manifest__.py
{
    'name': 'MRP Dry Product Consumption',
    'version': '1.0',
    'category': 'Manufacturing',
    'summary': 'Consume additional products if the produced product is dry.',
    'depends': ['mrp', 'stock'],
    'data': ['views/mrp_production_view.xml'],
    'installable': True,
    'application': False,
}