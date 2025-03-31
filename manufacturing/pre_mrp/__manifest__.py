# -*- coding: utf-8 -*-
{
    'name': "pre_mrp",

    'summary': """
     Pre manufacturing process""",

    'description': """
        This module allowes to create a manufacturing plan and quality test for it. it helps with companies which manufacture products bassed on client demand.
    """,

    'author': "Yoraki (Yeab A.)",
    'website': "https://www.yoraki.com",

   
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale_management','mail','mrp','stock','mrp_staging','quality'],

    # always loaded
    'data': [
        'security/group.xml',
        'security/ir.model.access.csv',
        
        "views/mrp_plan.xml",
        "views/mrp_plan_template.xml",
        
        "views/sales_order.xml",
        "views/menu.xml",
        
        
        "views/performa_invoice_template.xml",
        "views/report.xml",
        "views/mrp_production.xml",
        "views/grn_view.xml",
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    "application":True,
    "installable":True,
    # autoinstall dependencies
    "auto_install":True,
    "sequence":-2000
}
