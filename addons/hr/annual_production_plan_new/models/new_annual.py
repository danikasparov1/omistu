

from odoo import models, fields, api, _
from odoo.exceptions import UserError

# class AnnualProductionPlanBOMLine(models.Model):
#     _name = 'annual.production.plan.bom.line'
#     _description = 'Annual Production Plan BOM Line'

#     plan_id = fields.Many2one('annual.production.plan', string='Production Plan', ondelete='cascade')
#     component_id = fields.Many2one('product.product', string='Component', required=True)
#     component_name = fields.Char(string='Component Name', related='component_id.name', readonly=True, store=True)
#     quantity = fields.Float(string='Quantity', digits='Product Unit of Measure')
#     wastage_tolerance = fields.Float(string="Wastage Tolerance (%)", default=0.0)
#     consumed_quantity = fields.Float(
#         string="Consumed Quantity",
#         compute="_compute_consumed_quantity",
#         store=True,
#         help="Quantity consumed including wastage tolerance."
#     )

#     @api.depends('quantity', 'wastage_tolerance')
#     def _compute_consumed_quantity(self):
#         for line in self:
#             wastage_factor = 1 + (line.wastage_tolerance / 100)
#             line.consumed_quantity = line.quantity * wastage_factor

class AnnualProductionPlanBOMLine(models.Model):
    _name = 'annual.production.plan.bom.line'
    _description = 'Annual Production Plan BOM Line'

    plan_id = fields.Many2one('annual.production.plan', string='Production Plan', ondelete='cascade')
    component_id = fields.Many2one('product.product', string='Component', required=True)
    component_name = fields.Char(string='Component Name', related='component_id.name', readonly=True, store=True)
    quantity = fields.Float(string='Quantity', digits='Product Unit of Measure')
    wastage_tolerance = fields.Float(string="Wastage Tolerance (%)", default=0.0)
    consumed_quantity = fields.Float(
        string="Consumed Quantity",
        compute="_compute_consumed_quantity",
        store=True,
        help="Quantity consumed including wastage tolerance."
    )
    annual_planned_quantity = fields.Float(
        string="Annual Planned Qty",
        compute="_compute_annual_planned_quantity",
        help="Total quantity needed for the annual plan (consumed quantity × planned production)"
    )

    @api.depends('quantity', 'wastage_tolerance')
    def _compute_consumed_quantity(self):
        for line in self:
            wastage_factor = 1 + (line.wastage_tolerance / 100)
            line.consumed_quantity = line.quantity * wastage_factor

    @api.depends('consumed_quantity', 'plan_id.planned_quantity')
    def _compute_annual_planned_quantity(self):
        for line in self:
            line.annual_planned_quantity = line.consumed_quantity * line.plan_id.planned_quantity

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AnnualProductionPlan(models.Model):
    _name = 'annual.production.plan'
    _description = 'Annual Production Plan'

    name = fields.Char(string='Plan Name', required=True)
    year = fields.Integer(string='Year', required=True)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    planned_quantity = fields.Float(string='Planned Quantity', required=True)
    is_produced = fields.Boolean(string='Planned', compute='_compute_is_produced', store=True)
    bom_id = fields.Many2one('mrp.bom', string='BOM Reference', compute='_compute_bom_id')

    bom_component_ids = fields.One2many(
        'annual.production.plan.bom.line',
        'plan_id',
        string='BOM Components',
        readonly=False
    )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """Populate BOM components when a product is selected."""
        for record in self:
            # Clear existing components
            record.bom_component_ids = [(5, 0, 0)]

            if record.product_id:
                # Find the BOM for the selected product
                bom = self.env['mrp.bom'].search([
                    '|',
                    ('product_id', '=', record.product_id.id),
                    '&',
                    ('product_id', '=', False),
                    ('product_tmpl_id', '=', record.product_id.product_tmpl_id.id)
                ], order='product_id asc', limit=1)

                if bom:
                    # Populate BOM components
                    record.bom_component_ids = [(0, 0, {
                        'component_id': line.product_id.id,
                        'quantity': line.product_qty,
                        'wastage_tolerance': line.wastage_tolerance,
                    }) for line in bom.bom_line_ids]

    @api.model
    def create(self, vals):
        """Ensure BOM components are saved when creating a record."""
        record = super(AnnualProductionPlan, self).create(vals)
        if 'product_id' in vals:
            record._update_bom_components()
        return record

    def write(self, vals):
        """Ensure BOM components are saved when updating a record."""
        res = super(AnnualProductionPlan, self).write(vals)
        if 'product_id' in vals:
            self._update_bom_components()
        return res

    def _update_bom_components(self):
        """Update BOM components based on the selected product."""
        for record in self:
            if not record.product_id:
                continue

            # Find the BOM for the selected product
            bom = self.env['mrp.bom'].search([
                '|',
                ('product_id', '=', record.product_id.id),
                '&',
                ('product_id', '=', False),
                ('product_tmpl_id', '=', record.product_id.product_tmpl_id.id)
            ], order='product_id asc', limit=1)

            if bom:
                # Update BOM components
                record.bom_component_ids = [(5, 0, 0)] + [(0, 0, {
                    'component_id': line.product_id.id,
                    'quantity': line.product_qty,
                    'wastage_tolerance': line.wastage_tolerance,
                }) for line in bom.bom_line_ids]

    @api.depends('planned_quantity')
    def _compute_is_produced(self):
        for record in self:
            record.is_produced = record.planned_quantity > 0

    @api.depends('product_id')
    def _compute_bom_id(self):
        for record in self:
            record.bom_id = self.env['mrp.bom'].search([
                '|',
                ('product_id', '=', record.product_id.id),
                '&',
                ('product_id', '=', False),
                ('product_tmpl_id', '=', record.product_id.product_tmpl_id.id)
            ], order='product_id asc', limit=1)

    
    def action_view_purchases(self):
        self.ensure_one()
        component_ids = self.bom_component_ids.ids
        return {
            'name': _('Component Purchases'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order.line',
            'view_mode': 'tree,form',
            'domain': [('annual_plan_component_id', 'in', component_ids)],
            'context': {'create': False},
        }
    
    def action_view_stock_moves(self):
        self.ensure_one()
        component_ids = self.bom_component_ids.ids
        return {
            'name': _('Component Stock Moves'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.move',
            'view_mode': 'tree,form',
            'domain': [('annual_plan_component_id', 'in', component_ids)],
            'context': {'create': False},
        }

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def _update_raw_moves(self, bom_line, line_data):
        """
        Override to adjust the raw material consumption based on wastage tolerance.
        """
        # Calculate the adjusted quantity with wastage tolerance
        wastage_factor = 1 + (bom_line.wastage_tolerance / 100)
        adjusted_quantity = line_data['qty'] * wastage_factor

        # Update the quantity in the raw move
        line_data['qty'] = adjusted_quantity
        return super(MrpProduction, self)._update_raw_moves(bom_line, line_data)

    def action_confirm(self):
        """
        Override action_confirm to validate stock availability with wastage tolerance.
        """
        super(MrpProduction, self).action_confirm()

        for move in self.move_raw_ids:
            bom_line = move.bom_line_id
            if bom_line:
                # Calculate the adjusted quantity with wastage tolerance
                wastage_factor = 1 + (bom_line.wastage_tolerance / 100)
                adjusted_quantity = move.product_uom_qty * wastage_factor

                # Check stock availability
                if move.product_id.qty_available < adjusted_quantity:
                    raise UserError(_(
                        "Not enough stock for %s. Required: %s, Available: %s"
                    ) % (move.product_id.name, adjusted_quantity, move.product_id.qty_available))

                # Update the move with the adjusted quantity
                move.product_uom_qty = adjusted_quantity



from odoo import models, fields, api

class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    wastage_tolerance = fields.Float(
        string="Wastage Tolerance (%)",
        help="Percentage of material to account for possible wastage during production.",
        default=0.0,
    )

    consumed_quantity = fields.Float(
        string="Consumed Quantity",
        compute="_compute_consumed_quantity",
        store=True,
        help="Quantity consumed including wastage tolerance."
    )

    @api.depends('product_qty', 'wastage_tolerance')
    def _compute_consumed_quantity(self):
        for line in self:
            wastage_factor = 1 + (line.wastage_tolerance / 100)
            line.consumed_quantity = line.product_qty * wastage_factor
class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    reference_number = fields.Char(string="Reference Number")
