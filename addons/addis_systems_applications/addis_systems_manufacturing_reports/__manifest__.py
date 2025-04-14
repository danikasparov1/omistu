{
    "name": "Manufacturing Reports : Addis Systems",
    "version": "17.0.1.0",
    "sequence": 53,
    "summary": "Addis Systems Manufacturing Basic Reports",
    "description": """
        This Module is developed by Addis Systems for Basic Manufacturing Reports.
            ========================================
    """,
    "category": "Addis Systems/Manufacturing",
    "author": "Addis Systems/Beruk W.",
    "website": "https://www.addissystems.et/",
    "license": "LGPL-3",
    "depends": ["addis_systems_manufacturing_base", "addis_systems_manufacturing", "report_xlsx"],
    "external_dependencies": {"python": ["pulsar-client", "avro", "avro-schema"]},
    "data": [],
    "assets": {
        "web._assets_primary_variables": [],
        "web._assets_backend_helpers": [],
        "web.assets_backend": [],
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
    'auto_install': ["addis_systems_manufacturing_base", "addis_systems_manufacturing"],
}
