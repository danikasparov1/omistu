# -*- coding: utf-8 -*-
from odoo import models, fields, api

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    is_dry_product = fields.Boolean(string="Is Dry Product?", help="Check if the produced product is dry.")
    dry_consumed_product_id = fields.Many2one('product.product', string="Consumed Product",
                                              domain=[('type', '=', 'product')],
                                              help="Product that will be consumed when the produced product is dry.")
    dry_consumed_qty = fields.Float(string="Dry Consumed Quantity", compute="_compute_dry_consumed_qty", store=True)

    @api.depends('is_dry_product', 'product_qty')
    def _compute_dry_consumed_qty(self):
        for record in self:
            if record.is_dry_product and record.dry_consumed_product_id:
                record.dry_consumed_qty = record.product_qty * 0.0001
            else:
                record.dry_consumed_qty = 0

    def button_mark_done(self):
        """
        Override to consume additional product if the produced product is dry.
        """
        res = super(MrpProduction, self).button_mark_done()
        for record in self:
            if record.is_dry_product and record.dry_consumed_product_id:
                self.env['stock.move'].create({
                    'name': f'Consumption for {record.dry_consumed_product_id.name}',
                    'product_id': record.dry_consumed_product_id.id,
                    'product_uom_qty': record.dry_consumed_qty,
                    'product_uom': record.dry_consumed_product_id.uom_id.id,
                    'location_id': record.location_src_id.id,
                    'location_dest_id': record.location_dest_id.id,
                    'raw_material_production_id': record.id,
                    'state': 'done',
                })
        return res