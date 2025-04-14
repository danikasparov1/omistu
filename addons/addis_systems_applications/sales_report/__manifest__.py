{
    'name': "sales Report",
    'version': "17.0.0.1",
    'summary': """ HR Department module""",
    'description': """holds all hr module features""",
    'category': 'project',
    'depends': ['base', 'mrp'],

    'data': [
        'security/ir.model.access.csv',
        # 'data/data.xml',
        'wizard/project_report.xml',
        'report/report_template.xml',
        # 'views/payroll_report_header_footer.xml',

    ],
    'license': "AGPL-3",
    'installable': True,
    'application': True
}




