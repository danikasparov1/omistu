{
    "name": "Invoice Exchange",
    "version": "17.0.1.0",
    "sequence": 11,
    "summary": "Addis Systems Invoice Exchange",
    "description": """
        This is Addis Systems Invoice Exchange Module.
            ========================================
    """,
    "category": "Addis Systems/Accounting",
    "author": "Addis Systems/Beruk W.",
    "website": "https://www.addissystems.et/",
    "license": "LGPL-3",
    "depends": ["addis_systems_base", "addis_systems_accounting_base", "addis_systems_accounting_base", "point_of_sale", "account_edi_ubl_cii"],
    "external_dependencies": {"python": ["pulsar-client", "avro", "avro-schema"]},
    "data": [
        "views/AddisSystemsInvoices.xml",
        "data/InvoiceAndRefundData.xml"
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
