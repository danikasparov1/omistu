from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    annual_plan_component_id = fields.Many2one(
        'annual.production.plan.bom.line',
        string='Annual Plan Component',
        help="Link to the annual production plan component this purchase is for"
    )
    remaining_planned_qty = fields.Float(
        string="Remaining Planned Quantity",
        compute='_compute_remaining_planned_qty',
        store=True
    )
    adjustment_requested = fields.Boolean(
        string="Adjustment Requested",
        help="Indicates if this line exceeds planned quantity and requires approval"
    )
    adjustment_approved = fields.Boolean(
        string="Adjustment Approved",
        help="Indicates if the adjustment request was approved by GM"
    )

    @api.depends('annual_plan_component_id', 'product_qty')
    def _compute_remaining_planned_qty(self):
        for line in self:
            if line.annual_plan_component_id:
                # Calculate total purchased quantity for this component
                domain = [
                    ('annual_plan_component_id', '=', line.annual_plan_component_id.id),
                    ('state', 'in', ['purchase', 'done']),
                    ('id', '!=', line.id if line.id else False)
                ]
                purchased_qty = sum(self.search(domain).mapped('product_qty'))
                
                remaining = line.annual_plan_component_id.consumed_quantity - purchased_qty
                line.remaining_planned_qty = remaining - line.product_qty if line.id else remaining
            else:
                line.remaining_planned_qty = 0.0

    @api.constrains('product_qty')
    def _check_planned_quantity(self):
        for line in self:
            if line.annual_plan_component_id and not line.adjustment_approved:
                if line.product_qty > line.remaining_planned_qty + line.product_qty:
                    raise UserError(_(
                        "You cannot purchase more than the planned quantity (%s units remaining) without approval. "
                        "Please request an adjustment."
                    ) % line.remaining_planned_qty)

    def request_adjustment(self):
        """Action to request adjustment approval from GM"""
        for line in self:
            if line.remaining_planned_qty < 0:
                line.adjustment_requested = True
                # TODO: Implement notification to GM
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Adjustment Requested'),
                'message': _('Your adjustment request has been submitted for approval.'),
                'sticky': False,
            }
        }

class StockMove(models.Model):
    _inherit = 'stock.move'

    annual_plan_component_id = fields.Many2one(
        'annual.production.plan.bom.line',
        string='Annual Plan Component',
        help="Link to the annual production plan component this move is for"
    )

    def _action_confirm(self, merge=True, merge_into=False):
        """Override to check against planned quantities"""
        for move in self:
            if move.annual_plan_component_id:
                # Check if this is a procurement that exceeds planned quantity
                if move.product_uom_qty > move.annual_plan_component_id.remaining_planned_qty:
                    if not self.env.user.has_group('stock.group_stock_manager'):
                        raise UserError(_(
                            "This movement exceeds the planned quantity for %s. "
                            "Please request an adjustment from your manager."
                        ) % move.product_id.name)
        return super(StockMove, self)._action_confirm(merge=merge, merge_into=merge_into)

class AnnualProductionPlan(models.Model):
    _inherit = 'annual.production.plan'

    purchase_order_ids = fields.One2many(
        'purchase.order.line',
        compute='_compute_purchase_orders',
        string='Related Purchase Orders'
    )
    stock_move_ids = fields.One2many(
        'stock.move',
        compute='_compute_stock_moves',
        string='Related Stock Moves'
    )

    def _compute_purchase_orders(self):
        for plan in self:
            component_ids = plan.bom_component_ids.ids
            plan.purchase_order_ids = self.env['purchase.order.line'].search([
                ('annual_plan_component_id', 'in', component_ids)
            ])

    def _compute_stock_moves(self):
        for plan in self:
            component_ids = plan.bom_component_ids.ids
            plan.stock_move_ids = self.env['stock.move'].search([
                ('annual_plan_component_id', 'in', component_ids)
            ])

    def action_view_purchases(self):
        """Action to view related purchases"""
        self.ensure_one()
        return {
            'name': _('Purchase Orders'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order.line',
            'view_mode': 'tree,form',
            'domain': [('annual_plan_component_id', 'in', self.bom_component_ids.ids)],
            'context': {'create': False},
        }

    def action_view_stock_moves(self):
        """Action to view related stock moves"""
        self.ensure_one()
        return {
            'name': _('Stock Moves'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.move',
            'view_mode': 'tree,form',
            'domain': [('annual_plan_component_id', 'in', self.bom_component_ids.ids)],
            'context': {'create': False},
        }
    

class ProductProduct(models.Model):
    _inherit = 'product.product'

    annual_plan_info = fields.Text(
        string="Annual Production Plans",
        compute='_compute_annual_plan_info',
        help="Shows planned production quantities for this product"
    )

    def _compute_annual_plan_info(self):
        for product in self:
            plans = self.env['annual.production.plan'].search([
                ('product_id', '=', product.id)
            ])
            if not plans:
                product.annual_plan_info = "No annual production plans"
                continue
            
            info_lines = []
            for plan in plans:
                info_lines.append(
                    f"{plan.year}: Plan to produce {plan.planned_quantity} {product.uom_id.name}"
                )
            
            product.annual_plan_info = "\n".join(info_lines)


# from odoo import models, fields, api

# class ProductTemplate(models.Model):
#     _inherit = 'product.template'

#     annual_planned_quantity = fields.Float(
#         string='Annual Planned Quantity',
#         compute='_compute_annual_planned_quantity',
#         help="Total planned quantity from all annual production plans for this product"
#     )

#     def _compute_annual_planned_quantity(self):
#         plan_obj = self.env['annual.production.plan']
#         for template in self:
#             # Get all variant IDs
#             variant_ids = template.product_variant_ids.ids
#             # Search plans for any of these variants
#             plans = plan_obj.search([('product_id', 'in', variant_ids)])
#             template.annual_planned_quantity = sum(plans.mapped('planned_quantity'))


# class ProductProduct(models.Model):
#     _inherit = 'product.product'

#     annual_planned_quantity = fields.Float(
#         string='Annual Planned Quantity',
#         compute='_compute_annual_planned_quantity',
#         help="Total planned quantity from all annual production plans for this product"
#     )

#     def _compute_annual_planned_quantity(self):
#         plan_obj = self.env['annual.production.plan']
#         for product in self:
#             plans = plan_obj.search([('product_id', '=', product.id)])
#             product.annual_planned_quantity = sum(plans.mapped('planned_quantity'))


from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    annual_planned_quantity = fields.Float(
        string='Total Planned Quantity',
        compute='_compute_annual_planned_quantity',
        help="Total planned quantity (direct production + component usage)"
    )

    def _compute_annual_planned_quantity(self):
        plan_obj = self.env['annual.production.plan']
        for template in self:
            total = 0.0
            
            # 1. Direct plans (where this product is the main product)
            variant_ids = template.product_variant_ids.ids
            direct_plans = plan_obj.search([('product_id', 'in', variant_ids)])
            total += sum(direct_plans.mapped('planned_quantity'))
            
            # 2. Component usage (where this product is used in other plans)
            component_plans = plan_obj.search([])
            for plan in component_plans:
                for line in plan.bom_component_ids:
                    if line.component_id.product_tmpl_id == template:
                        total += line.consumed_quantity * plan.planned_quantity
            
            template.annual_planned_quantity = total


class ProductProduct(models.Model):
    _inherit = 'product.product'

    annual_planned_quantity = fields.Float(
        string='Total Planned Quantity',
        compute='_compute_annual_planned_quantity',
        help="Total planned quantity (direct production + component usage)"
    )

    def _compute_annual_planned_quantity(self):
        plan_obj = self.env['annual.production.plan']
        for product in self:
            total = 0.0
            
            # 1. Direct plans
            direct_plans = plan_obj.search([('product_id', '=', product.id)])
            total += sum(direct_plans.mapped('planned_quantity'))
            
            # 2. Component usage
            component_lines = self.env['annual.production.plan.bom.line'].search([
                ('component_id', '=', product.id)
            ])
            for line in component_lines:
                total += line.consumed_quantity * line.plan_id.planned_quantity
            
            product.annual_planned_quantity = total