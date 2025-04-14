{
    "name": "Addis Systems Payment Tax",
    "version": "17.0.1.0",
    "sequence": 50,
    "summary": "Addis Systems  Payment Tax",
    "description": """
        This Module is developed by Addis Systems for Basic Accounting Configurations and Modifications.
            ========================================
    """,
    "category": "Addis Systems/Accounting",
    "author": "Addis Systems/Abdulselam M.",
    "website": "https://www.addissystems.et/",
    "license": "LGPL-3",
    "depends": ["addis_systems_accounting_base",'account','account_payment'],
    "external_dependencies": {"python": ["pulsar-client", "avro", "avro-schema"]},
    "data": [
        "security/ir.model.access.csv",
        "views/account_tax.xml",
        "views/account_payment.xml"
      
    ],
    "assets": {
        "web._assets_primary_variables": [],
        "web._assets_backend_helpers": [],
        "web.assets_backend": [
            
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
