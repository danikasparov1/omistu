{
    'name': 'g2b beneficiary module',
    'version': '1.0',
    'summary': 'g2b beneficiary module',
    'sequence': 1,
    'description': """
        g2b beneficiary module Description
    """,
    'author': 'Yayal Abayneh',
    'depends': ['base','mail', 'product'],
     'data': [
         'security/ir.model.access.csv',
         'data/g2b_beneficiary_sequ_num.xml',
         'views/g2b_beneficiary_info_view.xml',
         'views/g2b_benefit_info_view.xml',
         'views/id_type_view.xml',
         'views/g2b_beneficiary_detail_view.xml',
         'views/g2b_package_line_view.xml',
         'views/g2b_beneficiary_category_view.xml',
         'views/menu.xml'
     ],
    'assets': {
        'web._assets_primary_variables': [
        ],
        'web.assets_backend': [
        ],
    },
    'installable': True,
    'auto_install': False,

}
           

        
