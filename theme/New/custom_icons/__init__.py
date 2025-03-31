
from odoo import models, api

def update_menu_icons(env):
    """Update menu icons for settings modules if installed."""
    menu_items = [
        {"xml_id": "base.menu_general_settings", "module": "base"},
        {"xml_id": "crm.res_config_settings_view_form", "module": "crm"},
        {"xml_id": "sale.res_config_settings_view_form", "module": "sale"},
        {"xml_id": "stock.res_config_settings_view_form", "module": "stock"},
        {"xml_id": "mrp.res_config_settings_view_form", "module": "mrp"},
        {"xml_id": "purchase.res_config_settings_view_form", "module": "purchase"},
        {"xml_id": "account.res_config_settings_view_form", "module": "account"},
        {"xml_id": "hr.res_config_settings_view_form", "module": "hr"},
        {"xml_id": "website.res_config_settings_view_form", "module": "website"},
        {"xml_id": "point_of_sale.res_config_settings_view_form", "module": "point_of_sale"},
    ]

    for item in menu_items:
        name = item["module"]
        menu_id = item["xml_id"]
        module_installed = env["ir.module.module"].search([
            ("name", "=", name),
            ("state", "=", "installed")
        ])
        if module_installed:
            menu = env.ref(menu_id, raise_if_not_found=False)
            if menu:
                menu.write({
                    "web_icon": f"custom_icons,static/src/img/icons/{name}.png",
                    "web_icon_data": f"background: url('/custom_icons/static/src/img/icons/{name}.png') no-repeat center; background-size: contain;"
                })

class SettingsMenuIconUpdater(models.Model):
    _name = "settings.menu.icon.updater"
    _description = "Update Icons for Settings Menus"

    @api.model
    def update_icons(self):
        update_menu_icons(self.env)
