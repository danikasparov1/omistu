{
    "name": "Inventory : Addis Systems",
    "version": "17.0.1.0",
    "sequence": 54,
    "summary": "Addis Systems Inventory/Stock Basic Configurations and Modifications",
    "description": """
        This Module is developed by Addis Systems for Basic Inventory/Stock Configurations and Modifications.
            ========================================
    """,
    "category": "Addis Systems/Inventory",
    "author": "Addis Systems/Beruk W.",
    "website": "https://www.addissystems.et/",
    "license": "LGPL-3",
    "depends": ["addis_systems_stock_base", "addis_systems_accounting", "addis_systems_accounting_reports"],
    "external_dependencies": {"python": ["pulsar-client", "avro", "avro-schema"]},
    "data": [
        "security/ir.model.access.csv",
        "data/sequence.xml",
        "views/action_request.xml",
        "views/stock_picking_views.xml",
        "views/customer_request.xml",
        "views/customer_request_template.xml",
        "views/customer_request_report_views.xml",
        "views/document_activity.xml",
        
        "data/AddisSystemsStockBaseReportsData.xml",
        "views/AddisSystemsStockPickingInheritedView.xml"
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
    'auto_install': False,
}
