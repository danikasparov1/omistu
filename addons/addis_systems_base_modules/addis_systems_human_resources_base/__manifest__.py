{
    "name": "Addis Systems Human Resources Base",
    "version": "17.0.1.0",
    "sequence": 4,
    "summary": "Addis Systems Human Resources Base",
    "description": """
        This is a Base Module for Addis Systems Human Resources Base.
            ========================================
    """,
    "category": "Addis Systems/Human Resources",
    "author": "Addis Systems/Beruk W.",
    "website": "https://www.addissystems.et/",
    "license": "LGPL-3",
    "depends": ["addis_systems_theme", "addis_systems_base", "hr", "hr_contract"],
    "external_dependencies": {"python": ["pulsar-client", "avro", "avro-schema"]},
    "data": [
        "data/AddisSystemsHRBasicData.xml"
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
    "application": False,
    'auto_install': ["addis_systems_theme", "addis_systems_base", "hr", "hr_contract"],
}
