

# from odoo import models, fields, api
# from odoo.exceptions import UserError
# import logging
# _logger = logging.getLogger(__name__)
# class MrpProductionStage(models.Model):
#     _name = 'mrp.production.stage'

#     name = fields.Char("Stage Name", required=True)
#     sequence = fields.Integer("Sequence", default=10)
#     task_ids = fields.One2many('mrp.production.task', 'stage_id', string="Tasks")
#     start_date = fields.Datetime("Start Date")
#     end_date = fields.Datetime("End Date")
#     product_id = fields.Many2one('mrp.production', string="Production Order", required=True)  # Corrected

#     milestone = fields.Boolean("Is Milestone?", default=False)

#     _order = 'sequence'


# class MrpProductionTask(models.Model):
#     _name = 'mrp.production.task'

#     name = fields.Char("Task Name", required=True)
#     stage_id = fields.Many2one('mrp.production.stage', string="Stage", ondelete='cascade')
#     material_ids = fields.Many2many('product.product', string="Materials")
#     machine_ids = fields.Many2many('mrp.machine', string="Machines")
#     assigned_to = fields.Many2one('hr.employee', string="Assigned To")
#     start_date = fields.Datetime("Start Date")
#     end_date = fields.Datetime("End Date")
#     status = fields.Selection([
#         ('not_started', 'Not Started'),
#         ('in_progress', 'In Progress'),
#         ('completed', 'Completed')
#     ], default='not_started', string="Status")
#     progress = fields.Float("Progress", compute='_compute_progress', store=True)

#     product_id = fields.Many2one('mrp.production', string="Production Order", required=True)  # Corrected

#     @api.depends('status')
#     def _compute_progress(self):
#         if self.status == 'completed':
#             self.progress = 100.0
#         elif self.status == 'in_progress':
#             self.progress = 50.0
#         else:
#             self.progress = 0.0
#     @api.model
#     def create(self, vals):
#         _logger.info("Creating record with values: %s", vals)
        
#         if 'product_id' in vals:
#             product_id = vals['product_id']
#             product = self.env['mrp.production'].browse(product_id)
#             if not product:
#                 raise UserError(f"Product ID {product_id} does not exist.")
        
#         return super(MrpProductionTask, self).create(vals)
#     @api.model
#     def check_material_availability(self):
#         for task in self:
#             for material in task.material_ids:
#                 stock_quantity = material.qty_available
#                 if stock_quantity <= 0:
#                     raise UserError(f"Material {material.name} is out of stock.")

#     def _check_delays(self):
#         for task in self:
#             if task.status != 'completed' and task.end_date < fields.Datetime.now():
#                 task.message_post(
#                     body="This task is delayed. Please review.",
#                     subtype='mail.mt_comment'
#                 )
# class MrpProduction(models.Model):
#     _inherit = 'mrp.production'

#     stage_ids = fields.One2many('mrp.production.stage', 'product_id', string="Production Stages")
#     task_ids = fields.One2many('mrp.production.task', 'product_id', string="Tasks")
#     progress = fields.Float("Overall Progress", compute='_compute_progress')

#     @api.depends('task_ids.progress')
#     def _compute_progress(self):
#         total_progress = 0
#         total_tasks = len(self.task_ids)
#         for task in self.task_ids:
#             total_progress += task.progress
#         if total_tasks > 0:
#             self.progress = total_progress / total_tasks
#         else:
#             self.progress = 0.0

#     def action_start_production(self):
#         for task in self.task_ids:
#             task.check_material_availability()

#         self.state = 'in_progress'
#         for task in self.task_ids:
#             task.status = 'in_progress'

#     def action_finish_production(self):
#         self.state = 'done'
#         for task in self.task_ids:
#             task.status = 'completed'

#     def action_cancel_production(self):
#         self.state = 'cancelled'
#         for task in self.task_ids:
#             task.status = 'not_started'
