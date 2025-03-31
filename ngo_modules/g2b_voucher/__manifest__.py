{
    'name': 'g2b voucher module',
    'version': '1.0',
    'summary': 'g2b voucher module',
    'sequence': 1,
    'description': """
        g2b voucher module Description
    """,
    'author': 'Yayal Abayneh',
    'depends': ['base','mail','g2b_beneficiary','g2b_provider'],
     'data': [
        'security/ir.model.access.csv',
         'data/g2b_voucher_sequ_num.xml',
         'views/g2b_voucher_info_view.xml',
         'views/g2b_generate_voucher_form.xml',
         'views/g2b_voucher_detail_view.xml',
         'views/g2b_voucher_amend_view.xml',
         'views/menu.xml',
         'report/g2b_voucher_print.xml',
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
           

        
