{
    "name": "Addis Systems Sales Base",
    "version": "17.0.1.0",
    "sequence": 9,
    "summary": "Addis Systems Sales Base",
    "description": """
        This is a Base Module for Addis Systems Sales Base.
            ========================================
    """,
    "category": "Addis Systems/Sales",
    "author": "Addis Systems/Beruk W.",
    "website": "https://www.addissystems.et/",
    "license": "LGPL-3",
    "depends": ["addis_systems_theme", "addis_systems_base", "addis_systems_stock_base", "sale_management"],
    "external_dependencies": {"python": ["pulsar-client", "avro", "avro-schema"]},
    "data": [
        "security/AddisSystemsSalesUserGroup.xml",
        "data/AddisSystemsSalesBaseData.xml"
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
    "pre_init_hook": "_pre_init_hook",
    # "post_init_hook": "_post_init_hook",
    "price": 49.99,
    "currency": "ETB",
    "application": False,
    'auto_install': ["addis_systems_theme", "addis_systems_base", "addis_systems_stock_base", "sale_management"],
}
