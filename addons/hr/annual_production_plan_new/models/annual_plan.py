
from odoo import models, fields, api

class AnnualProductionPlan(models.Model):
    _name = 'annual.production.plan'
    _description = 'Annual Production Plan'

    name = fields.Char(string='Plan Name', required=True)
    year = fields.Integer(string='Year', required=True)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    planned_quantity = fields.Float(string='Planned Quantity', required=True)
    is_produced = fields.Boolean(string='Produced', compute='_compute_is_produced', store=True)
    bom_component_ids = fields.One2many('annual.production.plan.bom.line', 'plan_id', string='BOM Components', compute='_compute_bom_components', store=False)

    @api.depends('product_id')
    def _compute_bom_components(self):
        for record in self:
            if record.product_id:
                # Find the BOM for the selected product
                bom = self.env['mrp.bom'].search([('product_id', '=', record.product_id.id)], limit=1)
                if not bom:
                    bom = self.env['mrp.bom'].search([('product_tmpl_id', '=', record.product_id.product_tmpl_id.id)], limit=1)

                # Populate the BOM components
                record.bom_component_ids = [(5, 0, 0)]  # Clear existing lines
                if bom:
                    record.bom_component_ids = [(0, 0, {
                        'component_id': line.product_id.id,
                        'component_name': line.product_id.name,
                        'quantity': line.product_qty,
                    }) for line in bom.bom_line_ids]
            else:
                record.bom_component_ids = [(5, 0, 0)]  # Clear if no product is selected

    @api.depends('planned_quantity', 'is_produced')
    def _compute_is_produced(self):
        for record in self:
            record.is_produced = record.planned_quantity > 0 and record.is_produced


class AnnualProductionPlanBOMLine(models.Model):
    _name = 'annual.production.plan.bom.line'
    _description = 'Annual Production Plan BOM Line'

    plan_id = fields.Many2one('annual.production.plan', string='Production Plan', ondelete='cascade')
    component_id = fields.Many2one('product.product', string='Component')
    component_name = fields.Char(string='Component Name', readonly=True)
    quantity = fields.Float(string='Quantity', readonly=True)

from odoo import models, fields

class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    wastage_tolerance = fields.Float(
        string="Wastage Tolerance (%)",
        help="Percentage of material to account for possible wastage during production.",
        default=0.0,
    )
