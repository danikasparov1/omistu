from odoo import api, fields, models, _
from odoo import osv
from odoo.exceptions import UserError


class PartnerGitlab(models.Model):
    _inherit = "res.partner"
    gitlab_username = fields.Char(string="Gitlab Username")