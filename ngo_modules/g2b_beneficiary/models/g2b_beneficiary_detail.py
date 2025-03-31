from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import re

LOCKED_FIELD_STATES = {
    state: [('readonly', True)]
    for state in {'done', 'cancel'}
}


class g2bBeneficiaryDetail(models.TransientModel):
    _name = "g2b.beneficiary.detail"
    _description = "g2b beneficiary detail"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    beneficiary_code = fields.Char(string="Code")
    name = fields.Char(string="Full name", readonly=True)
    id_type = fields.Many2one('g2b.id.type', string="Id type", readonly=True)
    category_id = fields.Many2one('g2b.beneficiary.category', string="Category",readonly=True)
    id_no = fields.Char(string="Id", readonly=True)
    phone = fields.Char(string="Phone", readonly=True)
    birth_date = fields.Datetime(string="Date of Birth", readonly=True)
    state = fields.Selection([
        ('registered', 'Registered'),
        ('confirmed', 'Confirmed'),
        ('canceled', 'Canceled')
    ], string='Status', default='registered', tracking=True)
    benefit_line1 = fields.One2many(
        comodel_name='g2b.benefit.detail.line',
        inverse_name='beneficiary_id',
        string="benefit List",
        states=LOCKED_FIELD_STATES,
        copy=True, auto_join=True)
    voucher_line1 = fields.One2many(
        comodel_name='g2b.voucher.detail.line',
        inverse_name='beneficiary_id',
        string="Voucher List",
        states=LOCKED_FIELD_STATES,
        copy=True, auto_join=True)
    image = fields.Binary(string="Image", readonly=True)
    region = fields.Char(string="Region", readonly=True)
    zone = fields.Char(string="Zone", readonly=True)
    woreda = fields.Char(string="Woreda", readonly=True)
    kebele = fields.Char(string="Kebele", readonly=True)


    def _featch_beneficiary_detail(self):
        for benfi in self:
            beneficiary = self.env['g2b.beneficiary.info'].search([('beneficiary_code', '=', benfi.beneficiary_code)],
                                                                  limit=1)
            if len(beneficiary) > 0:
                benfi.id_no = beneficiary.beneficiary_id
                benfi.name = beneficiary.name
                benfi.id_type = beneficiary.id_type
                benfi.phone = beneficiary.phone
                benfi.birth_date = beneficiary.birth_date
                benfi.state = beneficiary.state
                benfi.benefit_line1 = self._compute_benefit_list(beneficiary.benefit_line)
                benfi.voucher_line1 = self._compute_voucher_list(beneficiary.benefit_line)
                benfi.category_id = beneficiary.category_id

    def _compute_voucher_list(self, benefit_lines):
        voucher_lines=[]
        for ben in benefit_lines:
            voucher = self.env['g2b.voucher.info'].search([('benefit_id', '=', ben.benefit_id.id)],
                                                          limit=1)
            if len(voucher) > 0:
                voucher_lines.append((0, 0, {
                    'voucher': voucher.name,
                    'beneficiary': voucher.beneficiary_id.name,
                    'benefit_id': voucher.benefit_id.id,
                    'state': voucher.state,
                }))
        return voucher_lines

    def action_search_beneficiary(self):
        for rec in self:
            beneficiary = self.env['g2b.beneficiary.info'].search([('beneficiary_code', '=', rec.beneficiary_code)],
                                                                  limit=1)
            if len(beneficiary) == 0:
                raise ValidationError(_("Beneficiary With the Give Code doesn't exist"))
            else:
                rec._featch_beneficiary_detail()


    def _compute_benefit_list(self, benefit_lines):
        benefit_list=[]
        for ben in benefit_lines:
            benefit_list.append((0, 0, {
                'description': ben.benefit_id.name,
                'qty': ben.qty,
                'beneficiary': ben.beneficiary,
                'unit_price': ben.unit_price,
                'sub_total': ben.sub_total,
            }))
        return  benefit_list









