# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict
from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.fields import Command
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare, float_round


class g2bVoucherDetailLine(models.TransientModel):
    _name = 'g2b.voucher.detail.line'
    # _inherit = 'analytic.mixin'
    _description = "g2b.voucher.detail.line"
    voucher = fields.Char(string="Voucher Code")
    beneficiary = fields.Char(string="Beneficiary")
    beneficiary_id = fields.Many2one(
        comodel_name='g2b.beneficiary.detail',
        string="Beneficiary",
        ondelete='cascade', index=True, copy=False)

    benefit_id = fields.Many2one('g2b.benefit.info',
        string="Benefit",
        change_default=True, ondelete='restrict',  index='btree_not_null')
    state = fields.Selection([
        ('new', 'New'),
        ('confirmed', 'Confirmed'),
        ('redeemed', 'Redeemed'),
        ('canceled', 'Canceled'),
    ], string='State', default='new', tracking=True)



