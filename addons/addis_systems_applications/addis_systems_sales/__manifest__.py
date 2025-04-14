{
    "name": "Sales : Addis Systems",
    "version": "17.0.1.0",
    "sequence": 64,
    "summary": "Addis Systems Sales Basic Configurations and Modifications",
    "description": """
        This Module is developed by Addis Systems for Basic Sales Configurations and Modifications.
            ========================================
    """,
    "category": "Addis Systems/Sales",
    "author": "Addis Systems/Beruk W.",
    "website": "https://www.addissystems.et/",
    "license": "LGPL-3",
    "depends": ["addis_systems_sales_base", "base_vat", "sale_stock","product_expiry", "addis_systems_stock"],
    "data": [
        "views/sale_portal_template.xml",
        "views/AddisSystemsSalesInheritedView.xml",
        "data/thirdpartycmpany.xml",
        "views/res_partner_views.xml",
        "views/res_config_setting.xml",
        "data/sequence.xml",
        "views/third_party.xml",
        "views/withholding.xml"
    ],
    'assets': {
        'web.assets_backend': [
            'addis_systems_sales/static/src/widget/tin_number.xml',
            'addis_systems_sales/static/src/widget/tin_number.js',
            'addis_systems_sales/static/src/widget/tax_totals.js',

        ],
    },
    "installable": True,
    "price": 49.99,
    "currency": "ETB",
    "application": True,
    'auto_install': False,
}
