from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import re


LOCKED_FIELD_STATES = {
    state: [('readonly', True)]
    for state in {'done', 'cancel'}
}


class g2bBenefitInfo(models.Model):
    _name = "g2b.benefit.info"
    _description = "g2b benefit info"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    name = fields.Char(string="Name", required=True)
    description = fields.Char(string="Description")
    state = fields.Selection([
        ('done', 'Done'),
        ('cancel', 'Cancel'),
    ], string='State', default='done', required=True, tracking=True)
    package_line = fields.One2many(
        comodel_name='g2b.package.line',
        inverse_name='benefit_id',
        string="package List",
        states=LOCKED_FIELD_STATES,
        copy=True, auto_join=True)
    status = fields.Selection([
        ('new', 'New'),
        ('confirmed', 'Confirmed'),
        ('canceled', 'Canceled')
    ], string='Status', default='new', tracking=True)

    def confirm_status(self):
        for rec in self:
            rec.status='confirmed'






