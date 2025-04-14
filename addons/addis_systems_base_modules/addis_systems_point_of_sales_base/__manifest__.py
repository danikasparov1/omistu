{
    "name": "Addis Systems Point of Sales(PoS) Base",
    "version": "17.0.1.0",
    "sequence": 10,
    "summary": "Addis Systems Point of Sales(PoS) Base",
    "description": """
        This is a Base Module for Addis Systems Point of Sales(PoS) Base.
            ========================================
    """,
    "category": "Addis Systems/Point of Sale",
    "author": "Addis Systems/Beruk W.",
    "website": "https://www.addissystems.et/",
    "license": "LGPL-3",
    "depends": ["addis_systems_theme", "addis_systems_base", "addis_systems_sales_base", "addis_systems_accounting_base", "point_of_sale"],
    "external_dependencies": {"python": ["pulsar-client", "avro", "avro-schema"]},
    "data": [
        "security/AddisSystemsPointOfSalesUserGroup.xml",
        "data/AddisSystemsPoSBaseData.xml"
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
    'auto_install': ["addis_systems_theme", "addis_systems_base", "addis_systems_sales_base", "addis_systems_accounting_base", "point_of_sale"],
}
