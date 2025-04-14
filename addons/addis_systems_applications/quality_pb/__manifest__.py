# -*- coding: utf-8 -*-
{
    'name': "quality_pb",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'inventory_pb',
                'stock',
                'purchase'
                ],

    # always loaded
    "data": [
        
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/quality_data.xml",
        
        "views/views.xml",
        
        
        "views/stock_picking_views.xml",

# "#security/ir.model.access.csv",
        
        # "views/quality_views.xml"
        
        
        # "views/templates.xml",
        # "views/quality_test_type_views.xml"
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}
