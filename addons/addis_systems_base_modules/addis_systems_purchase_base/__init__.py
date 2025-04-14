

def _pre_init_hook(env):
    account_edi_ubl_cii = env["ir.module.module"].sudo().search([("name", "=", "account_edi_ubl_cii")])
    account_edi_ubl_cii.button_install()