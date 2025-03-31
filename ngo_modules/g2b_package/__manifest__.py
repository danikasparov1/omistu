{
    'name': 'g2b package module',
    'version': '1.0',
    'summary': 'g2b package module',
    'sequence': 1,
    'description': """
        g2b package module Description
    """,
    'author': 'Yayal Abayneh',
    'depends': ['base','mail','sale'],
     'data': [
        'security/ir.model.access.csv',
         'views/g2b_package_info_view.xml',
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
           

        
