{
    "name":"Addisystems Account Reconcillaion",
    "depends":["base","web","account"],
    "data":[
        "security/ir.model.access.csv",
        "views/account_move_line.xml",
        "views/reconcillation_filter_wizard.xml",
        "views/bank_statement.xml"

    ],
    "assets":{
        'web.assets_backend':[
            'addis_systems_reconcillation/static/src/view_inheritance/account_reconcile.js',
            'addis_systems_reconcillation/static/src/view_inheritance/account_reconcile.xml',
            
        ]
    }
}