{
    'name': 'AddisSystems Accounting Excel Reports',
    'author':'Addis Systems/Abdulselam M.',
    'version': '17.1',
    'summary': 'Reports',
    'sequence': -1000,
    'description': """AddisPay Report""",
    'category': 'report',
    'website': 'https://www.addissystems.et/',
    'depends': ['base','accounting_pdf_reports','om_account_daily_reports','report_xlsx'],
    'license': 'LGPL-3',
    "data":[
        "data/report.xml",
        "views/account_report_view.xml",
        "views/reports.xml"
    ],
    "assets": {
        "web.assets_backend": [

        ]

    }
}
