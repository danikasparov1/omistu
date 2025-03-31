# -*- coding: utf-8 -*-
{
    'name': "mrp_staging",

    'summary': """
       Manufacturing stages and steps per stage. """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Yoraki (Yeab A.)",
    'website': "https://www.yoraki.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mrp'],

    # always loaded
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',

        # 'views/settings_view.xml',
        'views/staging_config.xml',
        'views/mrp_production.xml',


    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application':True,
    'installable': True,
    'auto_install': False,
    'sequence': -3500
}
