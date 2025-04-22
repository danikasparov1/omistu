# from odoo import models, fields, api, _

# class AnnualProductionPlan(models.Model):
#     _name = 'annual.production.plan'
#     _description = 'Annual Production Plan'

#     name = fields.Char(string='Plan Name', required=True)
#     year = fields.Integer(string='Year', required=True)
#     product_id = fields.Many2one('product.product', string='Product', required=True)
#     planned_quantity = fields.Float(string='Planned Quantity', required=True)
#     is_produced = fields.Boolean(string='Produced', compute='_compute_is_produced', store=True)
#     bom_id = fields.Many2one('mrp.bom', string='BOM Reference', compute='_compute_bom_id')

#     bom_component_ids = fields.One2many(
#         'annual.production.plan.bom.line', 
#         'plan_id', 
#         string='BOM Components',
#         readonly=True  # Make it readonly to prevent manual changes
#     )

#     @api.model
#     def create(self, vals):
#         """ Override create to populate BOM components """
#         record = super(AnnualProductionPlan, self).create(vals)
#         if 'product_id' in vals:
#             record._update_bom_components()
#         return record

#     def write(self, vals):
#         """ Override write to update BOM components when product changes """
#         res = super(AnnualProductionPlan, self).write(vals)
#         if 'product_id' in vals:
#             self._update_bom_components()
#         return res

#     def _update_bom_components(self):
#         """ Update BOM components based on current product """
#         for record in self:
#             # Clear existing components
#             record.bom_component_ids.unlink()
            
#             if record.product_id:
#                 # Find the BOM for the selected product
#                 bom = self.env['mrp.bom'].search([
#                     '|',
#                     ('product_id', '=', record.product_id.id),
#                     '&',
#                     ('product_id', '=', False),
#                     ('product_tmpl_id', '=', record.product_id.product_tmpl_id.id)
#                 ], order='product_id asc', limit=1)

#                 if bom:
#                     # Create new component lines
#                     record.bom_component_ids = [(0, 0, {
#                         'component_id': line.product_id.id,
#                         'quantity': line.product_qty,
#                     }) for line in bom.bom_line_ids]

#     @api.depends('planned_quantity')
#     def _compute_is_produced(self):
#         for record in self:
#             record.is_produced = record.planned_quantity > 0



#     def _compute_bom_id(self):
#         for record in self:
#             record.bom_id = self.env['mrp.bom'].search([
#                 '|',
#                 ('product_id', '=', record.product_id.id),
#                 '&',
#                 ('product_id', '=', False),
#                 ('product_tmpl_id', '=', record.product_id.product_tmpl_id.id)
#             ], order='product_id asc', limit=1)

#     def action_view_bom(self):
#         self.ensure_one()
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'BOM',
#             'view_mode': 'form',
#             'res_model': 'mrp.bom',
#             'res_id': self.bom_id.id,
#         }


# class AnnualProductionPlanBOMLine(models.Model):
#     _name = 'annual.production.plan.bom.line'
#     _description = 'Annual Production Plan BOM Line'

#     plan_id = fields.Many2one('annual.production.plan', string='Production Plan', ondelete='cascade')
#     component_id = fields.Many2one('product.product', string='Component', required=True)
#     component_name = fields.Char(string='Component Name', related='component_id.name', readonly=True, store=True)
#     quantity = fields.Float(string='Quantity', required=True, digits='Product Unit of Measure')

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AnnualProductionPlan(models.Model):
    _name = 'annual.production.plan'
    _description = 'Annual Production Plan'

    name = fields.Char(string='Plan Name', required=True)
    year = fields.Integer(string='Year', required=True)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    planned_quantity = fields.Float(string='Planned Quantity', required=True)
    is_produced = fields.Boolean(string='Produced', compute='_compute_is_produced', store=True)
    bom_id = fields.Many2one('mrp.bom', string='BOM Reference', compute='_compute_bom_id')

    bom_component_ids = fields.One2many(
        'annual.production.plan.bom.line',
        'plan_id',
        string='BOM Components',
        readonly=False  # Allow saving the components
    )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """Update BOM components when the product is changed."""
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
                    # Create new component lines
                    record.bom_component_ids = [(0, 0, {
                        'component_id': line.product_id.id,
                        'quantity': line.product_qty,
                    }) for line in bom.bom_line_ids]

    @api.model
    def create(self, vals):
        """Override create to ensure BOM components are saved."""
        record = super(AnnualProductionPlan, self).create(vals)
        if 'product_id' in vals:
            record._update_bom_components()
        return record

    def write(self, vals):
        """Override write to ensure BOM components are saved."""
        res = super(AnnualProductionPlan, self).write(vals)
        if 'product_id' in vals:
            self._update_bom_components()
        return res

    def _update_bom_components(self):
        """Update BOM components based on the selected product."""
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
                    # Create new component lines
                    record.bom_component_ids = [(0, 0, {
                        'component_id': line.product_id.id,
                        'quantity': line.product_qty,
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

    def action_view_bom(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'BOM',
            'view_mode': 'form',
            'res_model': 'mrp.bom',
            'res_id': self.bom_id.id,
        }


class AnnualProductionPlanBOMLine(models.Model):
    _name = 'annual.production.plan.bom.line'
    _description = 'Annual Production Plan BOM Line'

    plan_id = fields.Many2one('annual.production.plan', string='Production Plan', ondelete='cascade')
    component_id = fields.Many2one('product.product', string='Component', required=True)
    component_name = fields.Char(string='Component Name', related='component_id.name', readonly=True, store=True)
    quantity = fields.Float(string='Quantity', required=True, digits='Product Unit of Measure')


# from odoo import models, fields

# class MrpBomLine(models.Model):
#     _inherit = 'mrp.bom.line'

#     wastage_tolerance = fields.Float(
#         string="Wastage Tolerance (%)",
#         help="Percentage of material to account for possible wastage during production.",
#         default=0.0,
#     )



class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    reference_number = fields.Char(string="Reference Number")

# class MrpProduction(models.Model):
#     _inherit = 'mrp.production'

#     def action_confirm(self):
#         super(MrpProduction, self).action_confirm()
#         for line in self.bom_id.bom_line_ids:
#             adjusted_quantity = line.product_qty * (1 - (line.wastage_tolerance / 100))
#             if line.product_id.qty_available < adjusted_quantity:
#                 raise UserError(_(
#                     "Not enough stock for %s. Required: %s, Available: %s"
#                 ) % (line.product_id.name, adjusted_quantity, line.product_id.qty_available))
#             # Deduct the adjusted quantity from inventory
#             line.product_id.sudo().write({
#                 'qty_available': line.product_id.qty_available - adjusted_quantity
#             })


from odoo import models, fields, api, _
from odoo.exceptions import UserError

# class MrpBomLine(models.Model):
#     _inherit = 'mrp.bom.line'

#     wastage_tolerance = fields.Float(
#         string="Wastage Tolerance (%)",
#         help="Percentage of material to account for possible wastage during production.",
#         default=0.0,
#     )

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