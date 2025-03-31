{
    'name': 'Custom Payroll Report',
    'version': '1.0',
    'summary': 'Custom Payroll Report',
    'sequence': 0,
    'description': """
        Custom Payroll Report module.
    """,

    'depends': ['base','hr_attendance','om_hr_payroll'],
     'data': [
         'security/ir.model.access.csv',
         'views/menu.xml',
         'views/custom_hr_payroll_report_view.xml',
         # 'views/custom_hr_payslip_run_view.xml',
         'views/request_payroll_report_form_view.xml',
         'views/custom_hr_contract.xml',
         'views/custom_hr_attendance.xml',





     ],
    'assets': {
        'web.assets_backend': [
               '/custom_sales/static/src/js/tree_view_redirect.js',
               # '/custom_sales/static/src/xml/sale_list_button.xml',
           ]
    },
    'installable': True,
    'auto_install': False,
}
           

        
