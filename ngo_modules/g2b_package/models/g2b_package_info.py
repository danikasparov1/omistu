from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class g2bPackageInfo(models.Model):
    _name = "g2b.package.info"
    _description = "g2b package info"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    name = fields.Char(string="Name", required=True)

