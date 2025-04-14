{
    'name': 'Dynamic Invoice Journals by Business Type',
    'version': '1.0',
    'depends': ['account', 'stock'],
    'author': 'Daniel',
    'category': 'Accounting',
    'description': """
        Customize invoice journal entries dynamically based on the business type:
        - Service
        - Wholesale/Retail
        - Manufacturing
    """,
    'data': [
        'views/res_company_views.xml',
    ],
    'installable': True,
    'application': False,
}
