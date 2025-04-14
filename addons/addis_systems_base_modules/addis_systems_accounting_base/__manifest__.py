{
    "name": "Addis Systems Accounting Base",
    "version": "17.0.1.0",
    "sequence": 6,
    "summary": "Addis Systems Accounting Base",
    "description": """
        This is a Base Module for Addis Systems Accounting Base.
            ========================================
    """,
    "category": "Addis Systems/Accounting",
    "author": "Addis Systems/Beruk W.",
    "website": "https://www.addissystems.et/",
    "license": "LGPL-3",
    "depends": ["addis_systems_theme", "addis_systems_base", "om_account_accountant", "account_edi_ubl_cii", "om_fiscal_year", "om_account_asset", "om_account_budget", "om_recurring_payments", "account_payment", "om_account_followup", "accounting_pdf_reports", "om_account_daily_reports"],
    "external_dependencies": {"python": ["pulsar-client", "avro", "avro-schema"]},
    "data": [
        "security/AddisSystemsAccountingUserGroup.xml",
        "data/AddisSystemsAccountingBaseData.xml"
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
    'auto_install': ["addis_systems_theme", "addis_systems_base", "om_account_accountant", "account_edi_ubl_cii", "om_fiscal_year", "om_account_asset", "om_account_budget", "om_recurring_payments", "account_payment", "om_account_followup", "accounting_pdf_reports", "om_account_daily_reports"],
}
