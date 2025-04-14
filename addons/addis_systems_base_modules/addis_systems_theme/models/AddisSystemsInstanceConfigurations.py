from odoo import models, fields, api
from odoo.http import request
import re


class AddisSystemsThemeDefinitionIrHttp(models.AbstractModel):
    _inherit = "ir.http"

    def session_info(self):
        result = super(AddisSystemsThemeDefinitionIrHttp, self).session_info()
        if request.env.user._is_internal():
            for company in request.env.user.company_ids.with_context(bin_size=True):
                result['user_companies']['allowed_companies'][company.id].update(
                    {'has_appsbar_image': bool(company.appbar_image)})
                result['user_companies']['allowed_companies'][company.id].update({
                    'has_background_image': bool(company.background_image),
                })
        return result


class AddisSystemsThemeDefinitionUsers(models.Model):
    _inherit = 'res.users'

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + ['sidebar_type']

    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS + ['sidebar_type']

    sidebar_type = fields.Selection(selection=[('invisible', 'Invisible'), ('small', 'Small'), ('large', 'Large')],
                                    string="Sidebar Type", default='invisible', required=True)


class AddisSystemsThemeDefinitionCompany(models.Model):
    _inherit = 'res.company'

    appbar_image = fields.Binary(string='Apps Menu Footer Image', attachment=True)
    favicon = fields.Binary(string="Company Favicon", attachment=True)
    background_image = fields.Binary(string='Apps Menu Background Image', attachment=True)


class AddisSystemsThemeDefinitionConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    @property
    def THEME_COLOR_FIELDS(self):
        return []

    @property
    def COLOR_ASSET_THEME_URL(self):
        return '/addis_systems_theme/static/src/scss/colors.scss'

    @property
    def COLOR_BUNDLE_THEME_NAME(self):
        return 'web._assets_primary_variables'

    appbar_image = fields.Binary(related='company_id.appbar_image', readonly=False)
    theme_favicon = fields.Binary(related='company_id.favicon', readonly=False)
    theme_background_image = fields.Binary(related='company_id.background_image', readonly=False)
    theme_color_appsmenu_text = fields.Char(string='Apps Menu Text Color')
    theme_color_appbar_text = fields.Char(string='AppsBar Text Color')
    theme_color_appbar_active = fields.Char(string='AppsBar Active Color')
    theme_color_appbar_background = fields.Char(string='AppsBar Background Color')

    def _get_theme_color_values(self):
        return self.env['web_editor.assets'].get_color_variables_values(self.COLOR_ASSET_THEME_URL,
                                                                        self.COLOR_BUNDLE_THEME_NAME,
                                                                        self.THEME_COLOR_FIELDS)

    def _set_theme_color_values(self, values):
        colors = self._get_theme_color_values()
        for var, value in colors.items():
            values[f'theme_{var}'] = value
        return values

    def _detect_theme_color_change(self):
        colors = self._get_theme_color_values()
        return any(self[f'theme_{var}'] != val for var, val in colors.items())

    def _replace_theme_color_values(self):
        variables = [{'name': field, 'value': self[f'theme_{field}']} for field in self.THEME_COLOR_FIELDS]
        return self.env['web_editor.assets'].replace_color_variables_values(self.COLOR_ASSET_THEME_URL,
                                                                            self.COLOR_BUNDLE_THEME_NAME, variables)

    def _reset_theme_color_assets(self):
        self.env['web_editor.assets'].reset_asset(self.COLOR_ASSET_THEME_URL, self.COLOR_BUNDLE_THEME_NAME)

    def action_reset_theme_color_assets(self):
        self._reset_light_color_assets()
        self._reset_dark_color_assets()
        self._reset_theme_color_assets()
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def get_values(self):
        res = super().get_values()
        res = self._set_theme_color_values(res)
        return res

    def set_values(self):
        res = super().set_values()
        if self._detect_theme_color_change():
            self._replace_theme_color_values()
        return res


class AddisSystemsThemeDefinitionScssEditor(models.AbstractModel):
    _inherit = 'web_editor.assets'

    def _get_color_variable(self, content, variable):
        value = re.search(fr'\$mk_{variable}\:?\s(.*?);', content)
        return value and value.group(1)

    def _get_color_variables(self, content, variables):
        return {var: self._get_color_variable(content, var) for var in variables}

    def _replace_color_variables(self, content, variables):
        for variable in variables:
            content = re.sub(fr'{variable["name"]}\:?\s(.*?);', f'{variable["name"]}: {variable["value"]};', content)
        return content

    def get_color_variables_values(self, url, bundle, variables):
        custom_url = self._make_custom_asset_url(url, bundle)
        content = self._get_content_from_url(custom_url)
        if not content:
            content = self._get_content_from_url(url)
        return self._get_color_variables(content.decode('utf-8'), variables)

    def replace_color_variables_values(self, url, bundle, variables):
        original = self._get_content_from_url(url).decode('utf-8')
        content = self._replace_color_variables(original, variables)
        self.with_context(set_color_variables=True).save_asset(url, bundle, content, 'scss')


class AddisSystemsThemeDefinitionView(models.Model):
    _inherit = "ir.ui.view"

    @api.model
    def _render_template(self, template, values=None):
        if template in ["web.login", "web.webclient_bootstrap"]:
            if self.env.company.name:
                values["title"] = str(self.env.company.name)
            else:
                values["title"] = "Addis Systems S.C."

            values["title"] = str(self.env.company.name)
        return super(AddisSystemsThemeDefinitionView, self)._render_template(template, values)
