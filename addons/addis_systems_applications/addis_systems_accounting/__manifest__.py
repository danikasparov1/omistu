{
    "name": "Addis Systems Accounting",
    "version": "17.0.1.0",
    "sequence": 50,
    "summary": "Addis Systems Accounting Basic Configurations and Modifications",
    "description": """
        This Module is developed by Addis Systems for Basic Accounting Configurations and Modifications.
            ========================================
    """,
    "category": "Addis Systems/Accounting",
    "author": "Addis Systems/Abdulselam M.",
    "website": "https://www.addissystems.et/",
    "license": "LGPL-3",
    "depends": ["addis_systems_accounting_base",'account','sale', 'stock_account','om_account_budget'],
    "external_dependencies": {"python": ["pulsar-client", "avro", "avro-schema"]},
    "data": [
        "security/ir.model.access.csv",
        #"views/account_portal_templates.xml",
        "views/account_budget_views.xml",
        "views/account_begining_balance.xml",
        "views/begining_move_form.xml",
        "views/account_init_view_readonly.xml"
    ],
    "assets": {
        "web._assets_primary_variables": [],
        "web._assets_backend_helpers": [],
        "web.assets_backend": [
            # 'addis_systems_accounting/static/src/src/begining_balance_widget/begining.xml',
            #  'addis_systems_accounting/static/src/src/begining_balance_widget/begining.js',
        ],
        
        "web.assets_frontend": [],
        "web.assets_tests": [],
        "web.qunit_suite_tests": [],
        "web.assets_qweb": [],
    },
    "demo": [],
    "installable": True,
    "price": 49.99,
    "currency": "ETB",
    "application": True,
    'auto_install': False,
}
