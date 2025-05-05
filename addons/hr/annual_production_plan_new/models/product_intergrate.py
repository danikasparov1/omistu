# from odoo import models, fields, api, _
# from odoo.exceptions import UserError

# class PurchaseOrderLine(models.Model):
#     _inherit = 'purchase.order.line'

#     annual_plan_component_id = fields.Many2one(
#         'annual.production.plan.bom.line',
#         string='Annual Plan Component',
#         help="Link to the annual production plan component this purchase is for"
#     )
#     remaining_planned_qty = fields.Float(
#         string="Remaining Planned Quantity",
#         compute='_compute_remaining_planned_qty',
#         store=True
#     )
#     adjustment_requested = fields.Boolean(
#         string="Adjustment Requested",
#         help="Indicates if this line exceeds planned quantity and requires approval"
#     )
#     adjustment_approved = fields.Boolean(
#         string="Adjustment Approved",
#         help="Indicates if the adjustment request was approved by GM"
#     )

#     @api.depends('annual_plan_component_id', 'product_qty')
#     def _compute_remaining_planned_qty(self):
#         for line in self:
#             if line.annual_plan_component_id:
#                 # Calculate total purchased quantity for this component
#                 domain = [
#                     ('annual_plan_component_id', '=', line.annual_plan_component_id.id),
#                     ('state', 'in', ['purchase', 'done']),
#                     ('id', '!=', line.id if line.id else False)
#                 ]
#                 purchased_qty = sum(self.search(domain).mapped('product_qty'))
                
#                 remaining = line.annual_plan_component_id.consumed_quantity - purchased_qty
#                 line.remaining_planned_qty = remaining - line.product_qty if line.id else remaining
#             else:
#                 line.remaining_planned_qty = 0.0

#     @api.constrains('product_qty')
#     def _check_planned_quantity(self):
#         for line in self:
#             if line.annual_plan_component_id and not line.adjustment_approved:
#                 if line.product_qty > line.remaining_planned_qty + line.product_qty:
#                     raise UserError(_(
#                         "You cannot purchase more than the planned quantity (%s units remaining) without approval. "
#                         "Please request an adjustment."
#                     ) % line.remaining_planned_qty)

#     def request_adjustment(self):
#         """Action to request adjustment approval from GM"""
#         for line in self:
#             if line.remaining_planned_qty < 0:
#                 line.adjustment_requested = True
#                 # TODO: Implement notification to GM
#         return {
#             'type': 'ir.actions.client',
#             'tag': 'display_notification',
#             'params': {
#                 'title': _('Adjustment Requested'),
#                 'message': _('Your adjustment request has been submitted for approval.'),
#                 'sticky': False,
#             }
#         }

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare

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
        store=True,
        digits='Product Unit of Measure'
    )
    adjustment_requested = fields.Boolean(
        string="Adjustment Requested",
        help="Indicates if this line exceeds planned quantity and requires approval"
    )
    adjustment_approved = fields.Boolean(
        string="Adjustment Approved",
        help="Indicates if the adjustment request was approved by GM"
    )

    @api.depends('annual_plan_component_id', 'product_qty', 'state')
    def _compute_remaining_planned_qty(self):
        for line in self:
            if line.annual_plan_component_id:
                component = line.annual_plan_component_id
                product = line.product_id
                
                # Get on-hand quantity
                on_hand = product.qty_available
                
                # Get all confirmed purchases for this component
                domain = [
                    ('annual_plan_component_id', '=', component.id),
                    ('state', 'in', ['purchase', 'done']),
                    ('id', '!=', line.id if line.id else False)
                ]
                purchased_qty = sum(self.search(domain).mapped('product_qty'))
                
                # Calculate remaining available quantity
                annual_planned_qty = component.annual_planned_quantity
                total_available = annual_planned_qty - on_hand - purchased_qty
                
                line.remaining_planned_qty = max(0, total_available - line.product_qty if line.id else total_available)
            else:
                line.remaining_planned_qty = 0.0

    @api.constrains('product_qty', 'annual_plan_component_id')
    def _check_planned_quantity(self):
        for line in self:
            if line.annual_plan_component_id and not line.adjustment_approved:
                component = line.annual_plan_component_id
                product = line.product_id
                
                on_hand = product.qty_available
                annual_planned_qty = component.annual_planned_quantity
                
                # Get all confirmed purchases excluding current line
                domain = [
                    ('annual_plan_component_id', '=', component.id),
                    ('state', 'in', ['purchase', 'done']),
                    ('id', '!=', line.id if line.id else False)
                ]
                purchased_qty = sum(self.search(domain).mapped('product_qty'))
                
                # Calculate if new purchase would exceed planned quantity
                if float_compare(
                    on_hand + purchased_qty + line.product_qty,
                    annual_planned_qty,
                    precision_digits=2
                ) > 0:
                    raise UserError(_(
                        "This purchase would exceed the annual planned quantity.\n\n"
                        "Product: %s\n"
                        "On Hand: %s\n"
                        "Already Purchased: %s\n"
                        "This Purchase: %s\n"
                        "Annual Planned Quantity: %s\n\n"
                        "Please request an adjustment if needed."
                    ) % (
                        product.display_name,
                        on_hand,
                        purchased_qty,
                        line.product_qty,
                        annual_planned_qty
                    ))

    def request_adjustment(self):
        """Action to request adjustment approval from GM"""
        for line in self:
            if line.remaining_planned_qty < 0:
                line.adjustment_requested = True
                # Send notification to GM
                self.env['mail.thread'].message_post(
                    partner_ids=[...],  # Add GM's partner ID here
                    body=_('Adjustment requested for purchase order line %s') % line.id,
                    subject=_('Purchase Quantity Adjustment Request')
                )
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


from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging
from odoo.tools.float_utils import float_compare
_logger = logging.getLogger(__name__)

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    annual_plan_component_id = fields.Many2one(
        'annual.production.plan.bom.line',
        string='Annual Plan Component',
        compute='_compute_annual_plan_component',
        store=True,
        readonly=False  # Important for manual override
    )

    @api.depends('product_id')
    def _compute_annual_plan_component(self):
        for line in self:
            if not line.product_id or line.annual_plan_component_id:
                continue
                
            # Find matching component line
            component_line = self.env['annual.production.plan.bom.line'].search([
                ('component_id', '=', line.product_id.id)
            ], limit=1)
            
            if component_line:
                line.annual_plan_component_id = component_line

    class PurchaseOrder(models.Model):
        _inherit = 'purchase.order'

        def button_confirm(self):
            # Validate quantities before confirming
            for order in self:
                for line in order.order_line:
                    if line.annual_plan_component_id:
                        component = line.annual_plan_component_id
                        product = line.product_id
                        
                        on_hand = product.qty_available
                        required = component.annual_planned_quantity
                        max_purchase = max(0, required - on_hand)
                        
                        if float_compare(line.product_qty, max_purchase, precision_digits=2) > 0:
                            raise ValidationError(_(
                                "Cannot confirm order: Quantity exceeds annual plan requirements.\n"
                                "Product: %s\n"
                                "Ordered: %s %s\n"
                                "Maximum Allowed: %s %s"
                            ) % (
                                product.display_name,
                                line.product_qty, product.uom_id.name,
                                max_purchase, product.uom_id.name
                            ))
            
            return super().button_confirm()
        

class AnnualProductionPlan(models.Model):
    _inherit = 'annual.production.plan'

    purchase_order_count = fields.Integer(
        compute='_compute_purchase_order_count',
        string='Purchase Orders'
    )

    def _compute_purchase_order_count(self):
        for plan in self:
            # Get all component lines for this plan
            component_lines = self.env['annual.production.plan.bom.line'].search([
                ('plan_id', '=', plan.id)
            ])
            
            # Count purchase order lines linked to these components
            plan.purchase_order_count = self.env['purchase.order.line'].search_count([
                ('annual_plan_component_id', 'in', component_lines.ids),
                ('state', '!=', 'cancel')  # Exclude canceled orders
            ])

    def action_view_purchase_orders(self):
        self.ensure_one()
        component_lines = self.env['annual.production.plan.bom.line'].search([
            ('plan_id', '=', self.id)
        ])
        lines = self.env['purchase.order.line'].search([
            ('annual_plan_component_id', 'in', component_lines.ids)
        ])
        orders = lines.mapped('order_id')
        
        return {
            'name': _('Purchase Orders'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', orders.ids)],
            'context': {'create': False},
        }
    

class ProductProduct(models.Model):
    _inherit = 'product.product'

    def action_view_annual_plan_purchases(self):
        self.ensure_one()
        component_lines = self.env['annual.production.plan.bom.line'].search([
            ('component_id', '=', self.id)
        ])
        lines = self.env['purchase.order.line'].search([
            ('annual_plan_component_id', 'in', component_lines.ids)
        ])
        orders = lines.mapped('order_id')
        
        return {
            'name': _('Annual Plan Purchases'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', orders.ids)],
            'context': {'create': False},
        }


class AnnualProductionPlan(models.Model):
    _inherit = 'annual.production.plan'
    
    @api.constrains('product_id')
    def _check_single_plan_per_product(self):
        for plan in self:
            existing_plans = self.search([
                ('product_id', '=', plan.product_id.id),
                ('id', '!=', plan.id)
            ])
            if existing_plans:
                raise ValidationError(
                    _("Product %s already has an annual production plan (%s). "
                      "Only one plan per product is allowed.") % 
                    (plan.product_id.display_name, existing_plans[0].name)
                )
            
class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.constrains('product_qty', 'annual_plan_component_id')
    def _check_purchase_quantity(self):
        for line in self:
            if not line.annual_plan_component_id:
                continue
                
            component = line.annual_plan_component_id
            product = line.product_id
            plan = component.plan_id
            
            # Calculate available quantity (planned - on hand - already purchased)
            on_hand = product.qty_available
            planned_qty = component.annual_planned_quantity * plan.planned_quantity
            
            # Get all existing purchase lines for this component
            existing_purchases = self.search([
                ('annual_plan_component_id', '=', component.id),
                ('state', 'in', ['purchase', 'done']),
                ('id', '!=', line.id)
            ])
            purchased_qty = sum(existing_purchases.mapped('product_qty'))
            
            available_qty = max(0, planned_qty - on_hand - purchased_qty)
            
            if float_compare(line.product_qty, available_qty, precision_digits=2) > 0:
                raise ValidationError(_(
                    "Cannot purchase more than available quantity for %s\n"
                    "Planned Quantity: %s\n"
                    "On Hand: %s\n"
                    "Already Purchased: %s\n"
                    "Available to Purchase: %s\n"
                    "Attempted to Purchase: %s"
                ) % (
                    product.display_name,
                    planned_qty,
                    on_hand,
                    purchased_qty,
                    available_qty,
                    line.product_qty
                ))

    @api.onchange('product_qty', 'product_id')
    def _onchange_check_quantity(self):
        if not self.annual_plan_component_id:
            return
            
        component = self.annual_plan_component_id
        product = self.product_id
        plan = component.plan_id
        
        on_hand = product.qty_available
        planned_qty = component.annual_planned_quantity * plan.planned_quantity
        
        existing_purchases = self.search([
            ('annual_plan_component_id', '=', component.id),
            ('state', 'in', ['purchase', 'done']),
            ('id', '!=', self._origin.id if self._origin else False)
        ])
        purchased_qty = sum(existing_purchases.mapped('product_qty'))
        
        available_qty = max(0, planned_qty - on_hand - purchased_qty)
        
        if float_compare(self.product_qty, available_qty, precision_digits=2) > 0:
            return {
                'warning': {
                    'title': _("Quantity Exceeds Available"),
                    'message': _(
                        "Available quantity to purchase: %s %s\n"
                        "You're attempting to purchase: %s %s"
                    ) % (
                        available_qty, product.uom_id.name,
                        self.product_qty, product.uom_id.name
                    )
                }
            }
        
class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def button_confirm(self):
        for order in self:
            for line in order.order_line:
                if line.annual_plan_component_id:
                    line._check_purchase_quantity()
        return super().button_confirm()
    

class AnnualProductionPlanBOMLine(models.Model):
    _inherit = 'annual.production.plan.bom.line'

    purchased_qty = fields.Float(
        string="Purchased Quantity",
        compute='_compute_purchased_qty',
        help="Quantity already purchased for this component"
    )

    def _compute_purchased_qty(self):
        for line in self:
            purchases = self.env['purchase.order.line'].search([
                ('annual_plan_component_id', '=', line.id),
                ('state', 'in', ['purchase', 'done'])
            ])
            line.purchased_qty = sum(purchases.mapped('product_qty'))