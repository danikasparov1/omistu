from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

LOCKED_FIELD_STATES = {
    state: [('readonly', True)]
    for state in {'done', 'cancel'}
}


class g2bVoucherDetail(models.TransientModel):
    _name = "g2b.voucher.detail"
    _description = "g2b voucher detail"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    name = fields.Char(string="Code", required=True)
    benefit_id = fields.Many2one('g2b.benefit.info', string="Benefit", readonly=True)
    beneficiary_id = fields.Many2one('g2b.beneficiary.info', string="Beneficiary", readonly=True)
    provider_id = fields.Many2one('g2b.provider.info', string="Provider")
    state = fields.Selection([
        ('new', 'New'),
        ('confirmed', 'Confirmed'),
        ('redeemed', 'Redeemed'),
        ('claimed', 'Claimed'),
        ('canceled', 'Canceled'),
    ], string='State', default='new',readonly=True, tracking=True)
    package_line = fields.One2many(
        comodel_name='g2b.voucher.detail.package.line',
        inverse_name='voucher_id',
        string="package List",
        # compute='_compute_package_line',
        states=LOCKED_FIELD_STATES,
        readonly=True,
        copy=True, auto_join=True)

    valid_from = fields.Datetime(string="Valid From", readonly=True,)
    valid_to = fields.Datetime(string="Valid To", readonly=True,)

    def action_redeemed_beneficiary(self):
        for rec in self:
            if not rec.provider_id:
                raise ValidationError(_("Please Select Provider"))
            vouchers = self.env['g2b.voucher.info'].search([('name','=', rec.name)])
            for voucher in vouchers:
                voucher.write({
                    'state': 'redeemed',
                    'provider_id': rec.provider_id
                })
            rec.state = "redeemed"
    def action_amend_voucher(self):
        for rec in self:
            voucher = self.env['g2b.voucher.info'].search([('name', '=', rec.name)], limit=1)
            return {
                'type': 'ir.actions.act_window',
                'name': 'Amend Voucher',
                'res_model': 'g2b.amend.voucher.form',
                'view_mode': 'form,tree',
                'target': 'new',
                'context': {
                    'default_voucher_id': voucher.id,
                }
            }


    def _compute_package_line(self, benefit_ids):
        voucher = []
        for pack in benefit_ids.package_line:
            voucher.append((0, 0, {
                'product_id': pack.product_id.id,
                'description': pack.description,
                'qty': pack.qty,
                'unit_price': pack.unit_price,
                'sub_total': pack.sub_total,
            }))
        return voucher


    def action_search_voucher(self):
        for rec in self:
            voucher = self.env['g2b.voucher.info'].search([('name', '=', rec.name)],
                                                          limit=1)
            if len(voucher) == 0:
                raise ValidationError(_("Voucher With the Give Code doesn't exist"))
            if len(voucher) > 0:
                rec.name=voucher.name
                rec.benefit_id=voucher.benefit_id
                rec.state=voucher.state
                rec.beneficiary_id=voucher.beneficiary_id
                rec.valid_from=voucher.valid_from
                rec.valid_to=voucher.valid_to
                rec.package_line=self._compute_package_line(voucher.benefit_id)





