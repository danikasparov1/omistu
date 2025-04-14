from . import models, controllers
import secrets
from odoo import tools, SUPERUSER_ID, Command
from odoo.exceptions import ValidationError, AccessError

import os
import requests
import asyncio
import logging
import subprocess

_logger = logging.getLogger(__name__)


# ----------------------- TODO -------------------------------
# Temporary Environment Variables Addis Systems ID
# ------------------------------------------------------------


def addis_systems_company_data(addis_systems_id, addis_systems_client_app_support_api, addis_systems_service_timeout):
    # ------------------------------------------------------------
    # Call Addis System Fastapi and get the Company Data and Structure
    # ------------------------------------------------------------

    url = f"{addis_systems_client_app_support_api}/AddisSystems/Base/CompanyInformation/{addis_systems_id}"
    return requests.get(url, timeout=addis_systems_service_timeout, headers={'content-type': 'application/json'})


def _main_company_data_check_and_restructure(env, main_company_data):
    # ------------------------------------------------------------
    # Check for the Main Company Data Structure and Validation
    # ------------------------------------------------------------

    mail_alias_domain = main_company_data.pop("mail_alias_domain")
    vat_registration_number = main_company_data.pop("vat_registration_number")
    if all(main_company_data[key] for key in main_company_data):
        main_company = {
            'name': str(main_company_data['company_name']),
            'currency_id': env['res.currency'].search(['|', ('name', '=', main_company_data['currency_code']), ('full_name', '=', main_company_data['currency_code'])], limit=1).id or env.ref('base.ETB', False).id,
            'country_id': env['res.country'].search(['|', ('name', '=', main_company_data['country_name']), ('code', '=', main_company_data['country_name'])], limit=1).id or env.ref('base.et', False).id,
            'state_id': env['res.country.state'].search(['|', ('name', '=', main_company_data['state_name']), ('code', '=', main_company_data['state_name'])], limit=1).id or env.ref('base.state_et_1', False).id,
            'city': main_company_data['city'],
            # TODO 'sub_city': main_company_data['city'],
            # TODO 'kebele': main_company_data['city'],
            'street2': main_company_data['street2'],
            'street': main_company_data['street'],
            'vat': main_company_data['tin_number'],
            'phone': main_company_data['phone'],
            'mobile': main_company_data['mobile'],
            'email': main_company_data['email'],
            'website': main_company_data['website'],
            'primary_color': main_company_data['primary_color'],
            'secondary_color': main_company_data['brand_color'],
        }

        if vat_registration_number:
            main_company['company_registry'] = str(vat_registration_number)

        return main_company if all(main_company[key] for key in main_company) else None


def _branch_company_data_check_and_restructure(env, branch_company_data):
    # ------------------------------------------------------------
    # Check for the Branch Main Companies Data Structure and Validation
    # ------------------------------------------------------------

    structured_branch_company_data = []
    base_company = env.ref('base.main_company')
    for branch in branch_company_data:
        vat_registration_number = branch.pop("vat_registration_number")
        if all(branch[key] for key in branch) and not env['res.company'].search([('name', '=', branch["branch_name"])]) and base_company.name == branch['main_branch_name']:
            branch_company = {
                'name': str(branch['branch_name']),
                'currency_id': env['res.currency'].search(['|', ('name', '=', branch['currency_code']), ('full_name', '=', branch['currency_code'])], limit=1).id or base_company.currency_id.id or env.ref('base.ETB', False).id,
                'country_id': env['res.country'].search(['|', ('name', '=', branch['country_name']), ('code', '=', branch['country_name'])], limit=1).id or base_company.country_id.id or env.ref('base.et', False).id,
                'state_id': env['res.country.state'].search(['|', ('name', '=', branch['state_name']), ('code', '=', branch['state_name'])], limit=1).id or base_company.state_id.id or env.ref('base.state_et_1', False).id,
                'city': branch['city'],
                # TODO 'sub_city': main_company_data['city'],
                # TODO 'kebele': main_company_data['city'],
                'street2': branch['street2'],
                'street': branch['street'],
                'vat': branch['tin_number'],
                'phone': branch['phone'],
                'mobile': branch['mobile'],
                'email': branch['email'],
                'website': branch['website'],
                "parent_id": env['res.company'].search([('name', '=', branch["main_branch_name"])], limit=1).id or base_company.id,
            }

            if vat_registration_number:
                branch_company['company_registry'] = str(vat_registration_number)

            if all(branch_company[key] for key in branch_company):
                structured_branch_company_data.append(branch_company)
    return structured_branch_company_data


def _pre_init_hook(env):
    # ------------------------------------------------------------
    # (pre-init) Set up Company information's and Administrator User to Addis Systems S.C Instance
    # ------------------------------------------------------------

    mail = env["ir.module.module"].sudo().search([("name", "=", "mail")])
    mail.sudo().button_install()
    contacts = env["ir.module.module"].sudo().search([("name", "=", "contacts")])
    contacts.sudo().button_install()
    auth_oauth = env["ir.module.module"].sudo().search([("name", "=", "auth_oauth")])
    auth_oauth.sudo().button_install()
    social_media = env["ir.module.module"].sudo().search([("name", "=", "social_media")])
    social_media.sudo().button_install()
    website = env["ir.module.module"].sudo().search([("name", "=", "website")])
    website.sudo().button_install()
    google_calendar = env["ir.module.module"].sudo().search([("name", "=", "google_calendar")])
    google_calendar.sudo().button_install()
    attachment_indexation = env["ir.module.module"].sudo().search([("name", "=", "attachment_indexation")])
    attachment_indexation.sudo().button_install()
    image_preview = env["ir.module.module"].sudo().search([("name", "=", "widget_preview_image")])
    image_preview.sudo().button_install()

    """addis_systems_id = tools.config['addis_systems_id']
    addis_systems_client_app_support_api = tools.config['addis_systems_client_application_support_api']
    addis_systems_service_timeout = int(tools.config['addis_systems_requests_timeout']) or 20

    response = addis_systems_company_data(addis_systems_id, addis_systems_client_app_support_api, addis_systems_service_timeout)

    if response.status_code == 200:
        company_initial_data = response.json()
        branch_company_ids = []

        # NOTE Main Company Configuration

        if company_initial_data and company_initial_data["main_company"] and company_initial_data["main_company"]['addis_system_id'] == str(addis_systems_id):

            # Restructure Main Company Data and Validate Mandatory Fields

            main_company_structured_data = _main_company_data_check_and_restructure(env, company_initial_data["main_company"])
            if main_company_structured_data and env.ref('base.main_company', False):
                base_company = env.ref('base.main_company')
                if base_company.name != main_company_structured_data['name'] or base_company.vat != main_company_structured_data['vat']:
                    base_company.write(main_company_structured_data)
                else:
                    _logger.info("Cannot install Addis System Base Modules because main company data received from addis systems client applications support services is not sufficient enough.")
            else:
                _logger.error("Cannot install Addis System Base Modules because main company data received from addis systems client applications support services is not sufficient.")
                raise ValidationError("Cannot install Addis System Base Modules because main company data received from addis systems client applications support services is not sufficient.")
        else:
            _logger.error("Cannot install Addis System Base Modules because couldn't get main company data from addis systems client applications support services.")
            raise ValidationError("Cannot install Addis System Base Modules because couldn't get main company data from addis systems client applications support services.")

        # NOTE Branch Company Configuration

        if company_initial_data and company_initial_data["branches"] and len(company_initial_data["branches"]) >= 1:
            branch_company_structured_data = _branch_company_data_check_and_restructure(env, company_initial_data["branches"])
            if branch_company_structured_data:
                for branch_data in branch_company_structured_data:
                    new_branch = env['res.company'].create(branch_data)
                    if new_branch.currency_id:
                        currency = env['res.currency'].browse(new_branch.currency_id.id)
                        if not currency.active:
                            currency.write({'active': True})

                    new_branch.write({'logo': new_branch.parent_id.logo})
                    branch_company_ids.append(new_branch.id)
                    _logger.info("New Branch Company have been created for Company %s", new_branch.partner_id.name)

        # NOTE Addis Systems Administrator User Configuration

        if company_initial_data and company_initial_data["administrator_user"] and (admin_user := env.ref('base.user_admin', False)):
            user_data = company_initial_data["administrator_user"]
            user_partner = admin_user.partner_id
            mandatory_keys = ['login', 'password', 'name']
            if all(user_data[key] for key in mandatory_keys):
                allowed_company_ids = admin_user.company_ids.ids + env['res.company'].search([('id', 'in', branch_company_ids)]).ids
                admin_user.write({
                    'name': user_data['name'],
                    'login': user_data['login'],
                    'password': user_data['password'],
                    'company_ids': list(set(allowed_company_ids))
                })
                user_partner.country_id = env['res.country'].search(['|', ('name', '=', user_data['country_name']), ('code', '=', user_data['country_name'])], limit=1).id or base_company.country_id.id or env.ref('base.et', False).id,
                user_partner.state_id = env['res.country.state'].search(['|', ('name', '=', user_data['state_name']), ('code', '=', user_data['state_name'])], limit=1).id or base_company.state_id.id or env.ref('base.state_et_1', False).id
                user_partner.city = user_data['city'] or user_partner.country_id
                user_partner.street2 = user_data['street2'] or user_partner.street2
                user_partner.street = user_data['street'] or user_partner.street
                user_partner.vat = user_data['tin_number'] or user_partner.vat
                user_partner.company_registry = user_data['vat_registration_number'] or user_partner.company_registry
                user_partner.phone = user_data['phone'] or user_partner.phone
                user_partner.mobile = user_data['mobile'] or user_partner.mobile
                user_partner.email = user_data['email'] or user_partner.email
                user_partner.website = user_data['website'] or user_partner.website
                user_partner.comment = user_data['contact_note'] or user_partner.comment

        # NOTE Addis Systems Bot Configuration

        if env.ref('base.partner_root', False):
            env.ref('base.partner_root').write({
                'name': 'AddisBot',
                'email': 'admin@addissystems.et',
                'company_id': env.ref('base.main_company', False).id
            })

        if env.ref('base.user_root', False):
            env.ref('base.user_root').write({
                'name': 'AddisBot',
                'partner_id': env.ref('base.partner_root', False).id,
                'email': 'admin@addissystems.et',
                'company_id': env.ref('base.main_company', False).id
            })
    else:
        _logger.error("Cannot install Addis System Base Modules because couldn't connect to addis systems client applications support services.")
        raise AccessError("Cannot install Addis System Base Modules because couldn't connect to addis systems client applications support services.")
"""


def _post_init_hook(env):
    # ------------------------------------------------------------
    # (post-init) Set up Addis Systems S.C Odoo Instance Dependencies and Extra Configurations
    # ------------------------------------------------------------

    for company in env["res.company"].sudo().search([]):
        company.external_report_layout_id = env.ref('addis_systems_theme.addis_systems_report').id
        report_layout_bold = env.ref('web.report_layout_bold').id
        company_doc = env["base.document.layout"].sudo().create({"report_layout_id": report_layout_bold, "company_id": company.id})
        company_doc.document_layout_save()

    ethiopia_account = env["ir.module.module"].sudo().search([("name", "=", "l10n_et")])
    ethiopia_account.button_install()

    if env.ref('base.main_company', False):
        env.ref('base.main_company').write({
            'name': 'Addis Systems S.C.',
            'currency_id': env.ref('base.ETB', False).id,
            'country_id': env.ref('base.et', False).id
        })
    env['ir.config_parameter'].set_param('google_calendar_client_id', '228998536287-a6aq552pk9m3pn3jcpb8h9v01qharvop.apps.googleusercontent.com')
    env['ir.config_parameter'].set_param('google_calendar_client_secret', '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Sample')

    """    response = addis_systems_company_data(tools.config['addis_systems_id'], tools.config['addis_systems_client_application_support_api'], int(tools.config['addis_systems_requests_timeout']) or 20)

    fields_look_up = env['res.company'].fields_get()
    main_company_data = response.json()['main_company'] if response.status_code == 200 else None
    if 'addis_system_id' in fields_look_up and env.ref('base.main_company') and main_company_data and main_company_data["addis_system_id"]:
        env.ref('base.main_company').addis_system_id = main_company_data["addis_system_id"]

    if 'trade_name' in fields_look_up and env.ref('base.main_company') and main_company_data and main_company_data["trade_name"]:
        env.ref('base.main_company').trade_name = main_company_data["trade_name"]

    if env.ref('base.main_company').country_id:
        env.ref('base.main_company').country_id.vat_label = "Tin Number"

    base_geolocalize = env["ir.module.module"].sudo().search([("name", "=", "base_geolocalize")])
    base_geolocalize.sudo().button_install()
"""


def _uninstall_cleanup(env):
    env["web_editor.assets"].reset_asset("/addis_systems_theme/static/src/colors.scss", "web._assets_primary_variables")
    env['res.config.settings']._reset_theme_color_assets()

