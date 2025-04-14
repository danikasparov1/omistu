def _pre_init_hook(env):
    account_edi_ubl_cii = env["ir.module.module"].sudo().search([("name", "=", "account_edi_ubl_cii")])
    account_edi_ubl_cii.button_install()
    product_images = env["ir.module.module"].sudo().search([("name", "=", "product_images")])
    product_images.button_install()
    stock_sms = env["ir.module.module"].sudo().search([("name", "=", "stock_sms")])
    stock_sms.button_install()
