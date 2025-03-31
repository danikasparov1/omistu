from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import re

LOCKED_FIELD_STATES = {
    state: [('readonly', True)]
    for state in {'done', 'cancel'}
}

class g2bBeneficiaryInfo(models.Model):
    _name = "g2b.beneficiary.info"
    _description = "g2b beneficiary info"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    beneficiary_code = fields.Char(string="Code", default=lambda self: _('New'), required=True)
    name = fields.Char(string="Full name", required=True)
    id_type = fields.Many2one('g2b.id.type', string="Id type", required=True)
    category_id = fields.Many2one('g2b.beneficiary.category', string="Category", required=True)
    beneficiary_id = fields.Char(string="Id", required=True)
    phone = fields.Char(string="Phone")
    birth_date = fields.Datetime(string="Date of Birth", required=True)
    state = fields.Selection([
        ('registered', 'Registered'),
        ('confirmed', 'Confirmed'),
        ('canceled', 'Canceled'),
        ('expired', 'Expired')
    ], string='Status', default='registered', tracking=True)
    image = fields.Binary(string="Image", attachment=True)
    benefit_line = fields.One2many(
        comodel_name='g2b.benefit.line',
        inverse_name='beneficiary_id',
        string="benefit List",
        states=LOCKED_FIELD_STATES,
        copy=True, auto_join=True)
    voucher_line = fields.One2many(
        comodel_name='g2b.voucher.line',
        inverse_name='beneficiary_id',
        string="Voucher List",
        states=LOCKED_FIELD_STATES,
        copy=True, auto_join=True)
    region = fields.Char(string="Region")
    zone = fields.Char(string="Zone")
    woreda = fields.Char(string="Woreda")
    kebele = fields.Char(string="Kebele")


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['beneficiary_code'] = self.env['ir.sequence'].next_by_code(
                'g2b.beneficiary.info') or _("New")

        return super().create(vals_list)

    def action_confirm_beneficiary(self):
        for rec in self:
            rec.state = "confirmed"

    @api.onchange('benefit_line')
    def _compute_voucher_list(self):
        for rec in self:
            voucher_lines = []
            for ben in rec.benefit_line:
                voucher = self.env['g2b.voucher.info'].search([('benefit_id', '=', ben.benefit_id.id)],
                                                              limit=1)
                if len(voucher) > 0:
                    voucher_lines.append((0, 0, {
                        'voucher': voucher.name,
                        'beneficiary': voucher.beneficiary_id.name,
                        'benefit_id': voucher.benefit_id.id,
                        'state': voucher.state,
                    }))
            rec.voucher_line = voucher_lines

    @api.constrains('phone')
    def _check_phone_number(self):
        for record in self:
            if record.phone and not re.match(r'^(09|07)[0-9]{8}$', record.phone):
                raise ValidationError(_("Phone number must have 10 numeric digits followed by two asterisks."))
            if record.phone[:2] not in ['09', '07', '+2']:
                raise ValidationError(_("Phone number must start with '09' or '07'."))

class g2IdType(models.Model):
    _name = "g2b.id.type"
    _description = "g2b id type"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    name = fields.Char(string="Id Type", required=True)
    description = fields.Char(string="Description")


class g2bBeneficiaryCategory(models.Model):
    _name = "g2b.beneficiary.category"
    _description = "g2b.beneficiary.category"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    name = fields.Char(string="Beneficiary Category", required=True)
    description = fields.Char(string="Description")
