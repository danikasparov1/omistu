from . import models, controllers, report


def _pre_init_hook(env):
    for company in env["res.company"].sudo().search([]):
        company.external_report_layout_id = env.ref('addis_systems_theme.addis_systems_report').id
        report_layout = env.ref('addis_systems_theme.report_layout_addis_systems').id
        company_doc = env["base.document.layout"].sudo().create({"report_layout_id": report_layout, "company_id": company.id})
        company_doc._onchange_logo()
        company_doc._get_asset_style()
        company_doc._onchange_company_id()
        company_doc._compute_logo_colors()
        company_doc.document_layout_save
        +6

    if env.ref("website.default_website"):
        # FIXME
        env.ref("website.default_website").domain = 'https://one.development.addissystems.primetechnologies.et/' or str(env['ir.config_parameter'].sudo().get_param('web.base.url'))

    l10n_et = env["ir.module.module"].sudo().search([("name", "=", "l10n_et")])
    l10n_et.button_install()
    mail_plugin = env["ir.module.module"].sudo().search([("name", "=", "mail_plugin")])
    mail_plugin.button_install()
    # report_xlsx = env["ir.module.module"].sudo().search([("name", "=", "report_xlsx")])
    # report_xlsx.button_install()


def _post_init_hook(env):
    # ---------------------------------------------------------------------------
    # Gets Subscription Level and modules to install Here
    # ---------------------------------------------------------------------------
    pass
