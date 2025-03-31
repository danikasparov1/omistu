# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict
from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.fields import Command
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare, float_round


class g2bBenefitDetailLine(models.TransientModel):
    _name = 'g2b.benefit.detail.line'
    # _inherit = 'analytic.mixin'
    _description = "g2b.benefit.detail.line"
    beneficiary_id = fields.Many2one(
        comodel_name='g2b.beneficiary.detail',
        string="Beneficiary",
        ondelete='cascade', index=True, copy=False)

    benefit_id = fields.Many2one('g2b.benefit.info',
        string="Benefit",
        change_default=True, ondelete='restrict',  index='btree_not_null')
    qty = fields.Float(string="Quantity", default=1.0)
    beneficiary = fields.Char(string="Beneficiary")
    description = fields.Char(string="Description")
    unit_price = fields.Float(string="Unit Price", default=1.0)
    sub_total = fields.Float(string="Subtotal", default=1.0)

    @api.onchange('qty', 'unit_price')
    def _compute_subtotal_price(self):
        for rec in self:
            rec.sub_total = rec.qty * rec.unit_price


