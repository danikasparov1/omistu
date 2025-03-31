{
    'name': 'g2b provider module',
    'version': '1.0',
    'summary': 'g2b provider module',
    'sequence': 1,
    'description': """
        g2b provider module Description
    """,
    'author': 'Yayal Abayneh',
    'depends': ['base','mail','product','g2b_beneficiary'],
     'data': [
         'security/ir.model.access.csv',
         'views/g2b_provider_info_view.xml',
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
           

        
