{
    'name': 'Manager Pre-Dashboard Module',
    'version': '1.0',
    'summary': 'Displays a pre-dashboard interface for managers',
    'category': 'Custom',
    'author': 'Daniel Tibebu',
    'website': 'https://addissystem.com',
    'depends': ['base', 'sale_management', 'account', 'stock','accounting_drill_down_report'],
    'data': [
        'security/ir.model.access.csv',
        'views/manager_dashboard_view.xml',
        'views/report_menu_view.xml',
        'views/task_menu_view.xml',
    ],

        'assets': {
        'web.assets_backend': [
            'manager_pre_dashboard/static/src/js/accounting_reports_popup.js',
            'manager_pre_dashboard/static/src/xml/accounting_reports_popup.xml',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
