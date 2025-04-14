{
    'name': 'Branch-Specific Manufacturing Management',
    'version': '1.0',
    'summary': 'Manage manufacturing orders and operations by branch.',
    'description': """
        Adds branch-specific functionality to manufacturing orders and operations:
        - Branch selection in manufacturing orders and work orders
        - Branch-level resource management and reporting
        - Role-based access control for branches
    """,
    'author': 'Daniel Tibebu',
    'depends': ['base', 'mrp'],
    'data': [
        'security/mrp_branch_security.xml',
        'security/ir.model.access.csv',
        'views/mrp_production_views.xml',
        'views/mrp_workorder_views.xml',
    ],
    'installable': True,
    'application': False,
}
