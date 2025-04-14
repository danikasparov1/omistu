{
    "name": "Addis Systems Connect with Peachtree",
    "version": "17.0.1.0",
    "sequence": 64,
    "summary": "Addis Systems Peach Tree Connection",
    "description": """
        This Module is developed by Addis Systems for connecting peachtree for parallel check.
            ========================================
    """,
    "category": "Addis Systems",
    "author": "Addis Systems/Abdulselam M.",
    "website": "https://www.addissystems.et/",
    "license": "LGPL-3",
    "depends": ["base","sale","account"],
    "data": [
        "views/export_view.xml",
    ],
    'assets': {
        'web.assets_backend': [
            "addis_systems_peachtree_integration/static/src/export_peachtree/export_xlsx.js",
            "addis_systems_peachtree_integration/static/src/export_peachtree/export_xlsx.xml"
        ],
    },
    "installable": True,
    "price": 49.99,
    "currency": "ETB",
    "application": True,
    'auto_install': False,
}
