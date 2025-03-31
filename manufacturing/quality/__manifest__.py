# -*- coding: utf-8 -*-
{
    'name': "Quality",

    'summary': """
      Manufacturing process quality testing.  with back and forth corrective maintenance on failed products """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Yeabsra A.",
    'website': "https://www.yoraki.com",
    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base','product','mrp','stock','maintenance'
                # 'acos_stock_request'
                ],

    'data': [
        # security files
        'security/quality_security.xml',
        'security/ir.model.access.csv',
        
        # view files
        # 'views/check_fields_view.xml',
        # 'views/check_state_view.xml',
        # 'views/stage_fields_view.xml',
        # 'views/quality_test_view.xml',
        # "views/qa.xml",
        # "views/stage_fields_new.xml",
        
        
        'views/menu.xml',
        "views/new/quality_assurance_view.xml",
        "views/new/quality_check_template.xml",
        "views/new/quality_test_instance_view.xml",
        "views/new/external_test.xml",
        "views/new/external_report_template.xml",
        "views/new/inherit_views.xml",
        # "views/new/res_config.xml"

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'images': ['static/description/icon.png'],
    

    'application':True,
    'installable': True,
    'auto_install': False,
    'sequence': -4500
}
