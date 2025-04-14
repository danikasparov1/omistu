

def _pre_init_hook(env):
    account_edi_ubl_cii = env["ir.module.module"].sudo().search([("name", "=", "account_edi_ubl_cii")])
    account_edi_ubl_cii.button_install()
    loyalty = env["ir.module.module"].sudo().search([("name", "=", "loyalty")])
    loyalty.button_install()
    sale_margin = env["ir.module.module"].sudo().search([("name", "=", "sale_margin")])
    sale_margin.button_install()
    delivery = env["ir.module.module"].sudo().search([("name", "=", "delivery")])
    delivery.button_install()