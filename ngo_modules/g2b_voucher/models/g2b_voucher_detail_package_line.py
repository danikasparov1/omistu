# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict
from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.fields import Command
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare, float_round


class g2bPackageDetailline(models.TransientModel):
    _name = 'g2b.voucher.detail.package.line'
    # _inherit = 'analytic.mixin'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "g2b.voucher.detail.package.info"
    voucher_id = fields.Many2one(
        comodel_name='g2b.voucher.detail',
        string="voucher",
        ondelete='cascade', index=True, copy=False)
    product_id = fields.Many2one('product.template',
        string="Product",
        change_default=True, ondelete='restrict',  index='btree_not_null')
    qty = fields.Float(string="Quantity", default=1.0)
    description = fields.Char(string="Description")
    unit_price = fields.Float(string="Unit Price", default=1.0)
    sub_total = fields.Float(string="Subtotal", default=1.0)

    @api.onchange('product_id')
    def _compute_unit_price(self):
        for rec in self:
            rec.unit_price = rec.product_id.list_price

    @api.onchange('qty', 'unit_price')
    def _compute_subtotal_price(self):
        for rec in self:
            rec.sub_total = rec.qty * rec.unit_price


