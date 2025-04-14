{
    "name": "Addis Systems Data PreProcessor",
    "version": "2.0",
    "sequence": 1,
    "summary": "Addis Systems Data PreProcessor",
    "description": """
        This is Addis Systems Data PreProcessor.
            ========================================
    """,
    "category": "Accounting/Localizations/Account Charts",
    "author": "Addis Systems/Abdulselam M.",
    "website": "https://www.addissystems.et/",
    "license": "LGPL-3",
    "depends": [
        "base",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/menu.xml",
        "views/main_menu.xml",
        "geneated_csv/report_financial_extended.xml",
        "geneated_csv/report_view.xml",
        "geneated_csv/action_all_rep.xml",
        "data/sequence.xml",
        #"views/account_tax_report_data.xml",
    ],
    "demo": [],
    "installable": True,
    "price": 49.99,
    "currency": "ETB",
    "application": True,
    "auto_install": False,
}
