from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class g2bGenerateVoucherForm(models.TransientModel):
    _name = 'g2b.generate.voucher.form'
    _description = 'G2b Generate Voucher Request form'
    date_from = fields.Date(string='Valid From', required=True)
    date_to = fields.Date(string='Valid To', required=True)
    category_id = fields.Many2one('g2b.beneficiary.category', string='Beneficiary Category', required=True)

    def compute_and_open_vouchers(self):
        for rec in self:
            self.env['g2b.voucher.info'].generate_voucher_by_category(rec.date_from, rec.date_to, rec.category_id)
            return {
                'type': 'ir.actions.act_window',
                'name': 'Voucher List',
                'res_model': 'g2b.voucher.info',
                'view_mode': 'tree,form,pivot',
                'target': 'current',
            }

