{
    "name":"Acconting Dynamic Report",
    "depends":[
        "base","web","account"
    ],
    "data":[
        "reports/financial_reports_views.xml",
        "reports/report_menu.xml",
        "reports/report_tax.xml",
        "reports/report_balance_sheet.xml",
        "reports/report_partner_ledgure.xml",
        "reports/report_profit_loss.xml",
        "reports/report_bank_book.xml",
        "reports/financial_reports_views.xml",
        'reports/report_cash_book.xml',
        'reports/report_general_ledgure.xml',
        'reports/report_trial_balance.xml',
        'reports/report_aged_payable.xml'


    ],

     "assets": {
        "web.assets_backend": [
        "accounting_drill_down_report/static/src/xml/base_report.xml",
        "accounting_drill_down_report/static/src/xml/tax_report.xml",
        "accounting_drill_down_report/static/src/xml/balance_sheet.xml",
        "accounting_drill_down_report/static/src/xml/partner_ledgure.xml",
        "accounting_drill_down_report/static/src/xml/profit_and_loss.xml",
        "accounting_drill_down_report/static/src/xml/bank_book.xml",
        "accounting_drill_down_report/static/src/xml/cash_book.xml",
        "accounting_drill_down_report/static/src/xml/aged_payable.xml",
        "accounting_drill_down_report/static/src/xml/general_ledgure.xml",
        "accounting_drill_down_report/static/src/xml/trial_balance.xml",




        "accounting_drill_down_report/static/src/js/partner_ledgure.js",
        "accounting_drill_down_report/static/src/js/base_report.js",
        "accounting_drill_down_report/static/src/js/balance_sheet.js",
        "accounting_drill_down_report/static/src/js/tax_report.js",
        "accounting_drill_down_report/static/src/js/profit_and_loss.js",
        "accounting_drill_down_report/static/src/js/bank_book.js",
        "accounting_drill_down_report/static/src/js/cash_book.js",
        "accounting_drill_down_report/static/src/js/aged_payable.js",
        "accounting_drill_down_report/static/src/js/general_ledgure.js",
        "accounting_drill_down_report/static/src/js/trial_balance.js",




        ]
     }
}