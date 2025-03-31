from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class g2bAmendVoucherForm(models.Model):
    _name = 'g2b.amend.voucher.form'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'G2b amend Voucher  form'
    _rec_name = 'voucher_id'
    voucher_id = fields.Many2one('g2b.voucher.info', string="voucher")
    provider_name = fields.Char(string="provider", compute='_compute_provider')
    beneficiary_name = fields.Char(string="Beneficiary", compute='_compute_provider')
    bank = fields.Char(string="Bank")
    account = fields.Char(string="Account")
    amount = fields.Char(string="Amount")

    @api.depends('voucher_id')
    def _compute_provider(self):
        for rec in self:
            total = 0
            if rec.voucher_id:
                for pro in rec.voucher_id.package_line:
                    total += (pro.qty * pro.unit_price)
                rec.provider_name = rec.voucher_id.provider_id.name
                rec.beneficiary_name = rec.voucher_id.beneficiary_id.name
            else:
                rec.provider_name = ""
                rec.beneficiary_name = ""
            rec.amount = total

    def compute_and_amend_vouchers(self):
        for rec in self:
            if not rec.voucher_id:
                raise ValidationError(_("Please Select voucher"))
            vouchers = self.env['g2b.voucher.info'].search([('id', '=', rec.voucher_id.id)])
            for voucher in vouchers:
                voucher.write({
                    'state': 'claimed',
                })
            return {
                'type': 'ir.actions.act_window',
                'name': 'Amend List',
                'res_model': 'g2b.amend.voucher.form',
                'view_mode': 'tree,form,pivot',
                'target': 'current',
            }

    def generate_voucher(self):
        # return self.env.ref('pad_ethiopia.payroll_report_report').with_context(landscape=True).report_action(self)
        return self.env.ref('g2b_voucher.generate_voucher_print_report_id').report_action(self)
