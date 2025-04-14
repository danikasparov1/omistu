{
    "name": "Addis Systems Website Base",
    "version": "17.0.1.0",
    "sequence": 3,
    "summary": "Addis Systems Website Base",
    "description": """
        This is a Base Module for Addis Systems Website Base.
            ========================================
    """,
    "category": "Addis Systems/Website",
    "author": "Addis Systems/Beruk W.",
    "website": "https://www.addissystems.et/",
    "license": "LGPL-3",
    "depends": ["addis_systems_theme", "addis_systems_base", "website"],
    "external_dependencies": {"python": ["pulsar-client", "avro", "avro-schema"]},
    "data": [
        "security/ir.model.access.csv",
        "data/AddisSystemsWebsiteBaseData.xml"
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
    "pre_init_hook": "_pre_init_hook",
    "post_init_hook": "_post_init_hook",
    "installable": True,
    "price": 49.99,
    "currency": "ETB",
    "application": False,
    'auto_install': ["addis_systems_theme", "addis_systems_base", "website"],
}
