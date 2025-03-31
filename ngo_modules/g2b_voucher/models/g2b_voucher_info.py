from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

LOCKED_FIELD_STATES = {
    state: [('readonly', True)]
    for state in {'done', 'cancel'}
}


class g2bVoucherInfo(models.Model):
    _name = "g2b.voucher.info"
    _description = "g2b voucher info"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    name = fields.Char(string="Code", required=True, default=lambda self: _('New'),)
    benefit_id = fields.Many2one('g2b.benefit.info', string="Benefit", required=True)
    beneficiary_id = fields.Many2one('g2b.beneficiary.info', string="Beneficiary", required=True)
    state = fields.Selection([
        ('new', 'New'),
        ('confirmed', 'Confirmed'),
        ('redeemed', 'Redeemed'),
        ('claimed', 'claimed'),
        ('canceled', 'Canceled'),
    ], string='State', default='new', tracking=True)
    package_line = fields.One2many(
        comodel_name='g2b.voucher.package.line',
        inverse_name='voucher_id',
        string="package List",
        compute='_compute_package_line',
        states=LOCKED_FIELD_STATES,
        copy=True, auto_join=True)

    valid_from = fields.Datetime(string="Valid From")
    valid_to = fields.Datetime(string="Valid To")
    provider_id = fields.Many2one('g2b.provider.info', string="Provider")



    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code('g2b.voucher.info') or _("New")
        return super().create(vals_list)

    def action_confirm_beneficiary(self):
        for rec in self:
            if rec.state == 'new':
                rec.state = "confirmed"

    def action_redeemed_beneficiary(self):
        for rec in self:
            rec.state = "redeemed"

    def action_canceled_beneficiary(self):
        for rec in self:
            rec.state = "canceled"

    # @api.onchange('benefit_id')
    # def compute_packages_beneficiary(self):
    #     for rec in self:
    #         rec.package_line = rec.benefit_id.package_line

    def generate_voucher_by_category(self, start, end, category):
        beneficiarys = self.env['g2b.beneficiary.info'].search(
            [('category_id', '=', category.id), ('state', '=', 'confirmed')])
        if beneficiarys:
            for beneficiary in beneficiarys:
                for benefit in beneficiary.benefit_line:
                    self.env['g2b.voucher.info'].sudo().create({
                        'benefit_id': benefit.benefit_id.id,
                        'beneficiary_id': beneficiary.id,
                        'state': 'new',
                        'valid_from': start,
                        'valid_to': end
                    })

    @api.depends('benefit_id')
    def _compute_package_line(self):
        for rec in self:
            voucher = []
            for pack in rec.benefit_id.package_line:
                voucher.append((0, 0, {
                    'product_id': pack.product_id.id,
                    'description': pack.description,
                    'qty': pack.qty,
                    'unit_price': pack.unit_price,
                    'sub_total': pack.sub_total,
                }))
            rec.package_line=voucher





