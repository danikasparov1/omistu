{
    "name": "Addis Systems Inventory Base",
    "version": "17.0.1.0",
    "sequence": 7,
    "summary": "Addis Systems Inventory Base",
    "description": """
        This is a Base Module for Addis Systems Inventory Base.
            ========================================
    """,
    "category": "Addis Systems/Inventory",
    "author": "Addis Systems/Beruk W.",
    "website": "https://www.addissystems.et/",
    "license": "LGPL-3",
    "depends": ["addis_systems_theme", "addis_systems_base", "stock"],
    "external_dependencies": {"python": ["pulsar-client", "avro", "avro-schema"]},
    "data": [
        "security/ir.model.access.csv",
        "security/AddisSystemsStockUserGroup.xml",
        "data/AddisSystemsStockBaseData.xml"
    ],
    "assets": {
        "web._assets_primary_variables": [],
        "web._assets_backend_helpers": [],
        "web.assets_backend": [
            "addis_systems_stock_base/static/src/xml/AddisSystemsInventoryReportExcelOption.xml"
        ],
        "web.assets_frontend": [],
        "web.assets_tests": [],
        "web.qunit_suite_tests": [],
        "web.assets_qweb": [],
    },
    "demo": [],
    "pre_init_hook": "_pre_init_hook",
    # "post_init_hook": "_post_init_hook",
    "installable": True,
    "price": 49.99,
    "currency": "ETB",
    "application": False,
    'auto_install': ["addis_systems_theme", "addis_systems_base", "stock"],
}
