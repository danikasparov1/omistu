# # from odoo import models, fields, api

# # class AnnualProductionPlan(models.Model):
# #     _name = 'annual.production.plan'
# #     _description = 'Annual Production Plan'

# #     name = fields.Char(string='Plan Name', required=True)
# #     year = fields.Integer(string='Year', required=True)
# #     product_id = fields.Many2one('product.product', string='Product', required=True)
# #     planned_quantity = fields.Float(string='Planned Quantity', required=True)
# #     produced_quantity = fields.Float(string='Produced Quantity', compute='_compute_produced_quantity', store=True)
# #     is_produced = fields.Boolean(string='Produced', compute='_compute_is_produced', store=True)
# #     status_notification = fields.Char(string='Status Notification', compute='_compute_status_notification', store=True)

# #     @api.depends('product_id', 'year')
# #     def _compute_produced_quantity(self):
# #         for record in self:
# #             # Compute the produced quantity based on manufacturing orders
# #             produced_qty = self.env['mrp.production'].search([ 
# #                 ('product_id', '=', record.product_id.id),
# #                 ('date_planned_start', '>=', f'{record.year}-01-01'),
# #                 ('date_planned_start', '<=', f'{record.year}-12-31'),
# #                 ('state', '=', 'done')
# #             ]).mapped('product_qty')
# #             record.produced_quantity = sum(produced_qty)

# #     @api.depends('planned_quantity', 'produced_quantity')
# #     def _compute_is_produced(self):
# #         for record in self:
# #             record.is_produced = record.produced_quantity >= record.planned_quantity

# #     @api.depends('produced_quantity', 'planned_quantity')
# #     def _compute_status_notification(self):
# #         for record in self:
# #             if record.produced_quantity < record.planned_quantity:
# #                 record.status_notification = "Produced quantity is less than planned"
# #             else:
# #                 record.status_notification = "Production plan achieved"



# from odoo import models, fields, api

# class AnnualProductionPlan(models.Model):
#     _name = 'annual.production.plan'
#     _description = 'Annual Production Plan'

#     name = fields.Char(string='Plan Name', required=True)
#     year = fields.Integer(string='Year', required=True)
#     product_id = fields.Many2one('product.product', string='Product', required=True)
#     planned_quantity = fields.Float(string='Planned Quantity', required=True)
#     produced_quantity = fields.Float(string='Produced Quantity', compute='_compute_produced_quantity', store=True)
#     is_produced = fields.Boolean(string='Produced', compute='_compute_is_produced', store=True)
#     status_notification = fields.Char(string='Status Notification', compute='_compute_status_notification', store=True)

#     @api.depends('product_id', 'year')
#     def _compute_produced_quantity(self):
#         for record in self:
#             # Compute the produced quantity based on manufacturing orders
#             produced_qty = self.env['mrp.production'].search([
#                 ('product_id', '=', record.product_id.id),
#                 # ('date_start', '>=', f'{record.year}),
#                 # ('date_start', '<=', f'{record.year}),
#                 ('state', '=', 'done')
#             ]).mapped('product_qty')
#             record.produced_quantity = sum(produced_qty)

#     @api.depends('planned_quantity', 'produced_quantity')
#     def _compute_is_produced(self):
#         for record in self:
#             record.is_produced = record.produced_quantity >= record.planned_quantity

#     @api.depends('produced_quantity', 'planned_quantity')
#     def _compute_status_notification(self):
#         for record in self:
#             if record.produced_quantity < record.planned_quantity:
#                 record.status_notification = "Produced quantity is less than planned"
#             else:
#                 record.status_notification = "Production plan achieved"



from odoo import models, fields, api

class AnnualProductionPlan(models.Model):
    _name = 'annual.production.plan'
    _description = 'Annual Production Plan'

    name = fields.Char(string='Plan Name', required=True)
    year = fields.Integer(string='Year', required=True)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    planned_quantity = fields.Float(string='Planned Quantity', required=True)
    # produced_quantity = fields.Float(string='Produced Quantity', compute='_compute_produced_quantity', store=True)
    is_produced = fields.Boolean(string='Produced as expected', store=True)
    produced_quantity = fields.Float(string='Produced Quantity')
    # status_notification = fields.Char(string='Status Notification', compute='_compute_status_notification', store=True)

    # @api.depends('product_id', 'year')
    # def _compute_produced_quantity(self):
    #     for record in self:
    #         if not record.product_id or not record.year:
    #             record.produced_quantity = 0
    #             continue
            
    #         produced_qty = self.env['mrp.production'].search([(
    #             'product_id', '=', record.product_id.id),
    #             ('date_planned_start', '>=', f'{record.year}-01-01'),
    #             ('date_planned_start', '<=', f'{record.year}-12-31'),
    #             ('state', '=', 'done')
    #         ]).mapped('product_qty')
    #         record.produced_quantity = sum(produced_qty)

    # @api.depends('planned_quantity', 'produced_quantity')
    # def _compute_is_produced(self):
    #     for record in self:
    #         record.is_produced = record.produced_quantity >= record.planned_quantity if record.planned_quantity else False

    # @api.depends('produced_quantity', 'planned_quantity')
    # def _compute_status_notification(self):
    #     for record in self:
    #         if record.produced_quantity < record.planned_quantity:
    #             record.status_notification = "Produced quantity is less than planned"
    #         else:
    #             record.status_notification = "Production plan achieved"
