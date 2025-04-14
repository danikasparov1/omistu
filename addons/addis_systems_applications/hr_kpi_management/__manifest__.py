# __manifest__.py
{
    'name': 'HR KPI Management NEW',
    'version': '1.0',
    'summary': 'Manage and evaluate employee KPIs',
    'category': 'Human Resources',
    'author': 'Your Name',
    'depends': ['hr'],
    'data': [
        
        'views/kpi_view.xml',
        'views/kpi_evaluation_view.xml',
        # 'views/menus.xml',
        'security/ir.model.access.csv',
        # 'reports/kpi_report.xml',
        # 'reports/kpi_report_template.xml',
        # 'data/kpi_data.xml',
    ],
    'installable': True,
    'application': True,
}