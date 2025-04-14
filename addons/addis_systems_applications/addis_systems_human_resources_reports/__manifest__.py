{
    "name": "Human Resources Reports : Addis Systems",
    "version": "17.0.1.0",
    "sequence": 57,
    "summary": "Addis Systems Human Resources Basic Reports",
    "description": """
        This Module is developed by Addis Systems for Basic Human Resources Reports.
            ========================================
    """,
    "category": "Addis Systems/Human Resources",
    "author": "Addis Systems/Beruk W.",
    "website": "https://www.addissystems.et/",
    "license": "LGPL-3",
    "depends": ["addis_systems_human_resources_base", "addis_systems_human_resources", "report_xlsx"],
    "external_dependencies": {"python": ["pulsar-client", "avro", "avro-schema"]},
    "data": [
    ],
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
    'auto_install': ["addis_systems_human_resources_base", "addis_systems_human_resources"],
}
