# from odoo import models, fields, api

# class ManagerDashboard(models.TransientModel):
#     _name = 'manager.dashboard'
#     _description = 'Pre-Dashboard for Managers'

#     sales_count = fields.Integer(string="Sales Count", compute="_compute_sales_count")
#     purchase_count = fields.Integer(string="Purchase Count", compute="_compute_purchase_count")
#     task_count = fields.Integer(string="Tasks Pending Approval", compute="_compute_task_count")

#     @api.depends()
#     def _compute_sales_count(self):
#         self.sales_count = self.env['sale.order'].search_count([('state', 'in', ['sale', 'done'])])

#     @api.depends()
#     def _compute_purchase_count(self):
#         self.purchase_count = self.env['purchase.order'].search_count([('state', 'in', ['purchase', 'done'])])

#     @api.depends()
#     def _compute_task_count(self):
#         self.task_count = self.env['sale.order'].search_count([('state', '=', 'sent')])

#     def open_reports_menu(self):
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Reports',
#             'view_mode': 'tree',
#             'res_model': 'sale.report',
#             'target': 'current',
#         }

#     def open_tasks_menu(self):
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Tasks',
#             'view_mode': 'tree',
#             'res_model': 'sale.order',
#             'domain': [('state', '=', 'sent')],
#             'target': 'current',
#         }

#     def open_purchase_reports(self):
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Purchase Reports',
#             'view_mode': 'tree',
#             'res_model': 'purchase.report',
#             'target': 'current',
#         }

#     def open_inventory_reports(self):
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Inventory Reports',
#             'view_mode': 'tree',
#             'res_model': 'stock.report',
#             'target': 'current',
#         }


from odoo import models, fields, api

class ManagerDashboard(models.TransientModel):
    _name = 'manager.dashboard'
    _description = 'Pre-Dashboard for Managers'

    sales_count = fields.Integer(string="Sales Count", compute="_compute_sales_count")
    purchase_count = fields.Integer(string="Purchase Count", compute="_compute_purchase_count")
    task_count = fields.Integer(string="Tasks Pending Approval", compute="_compute_task_count")

    @api.depends()
    def _compute_sales_count(self):
        self.sales_count = self.env['sale.order'].search_count([('state', 'in', ['sale', 'done'])])

    @api.depends()
    def _compute_purchase_count(self):
        self.purchase_count = self.env['purchase.order'].search_count([('state', 'in', ['purchase', 'done'])])

    @api.depends()
    def _compute_task_count(self):
        self.task_count = self.env['sale.order'].search_count([('state', '=', 'sent')])

    def open_reports_menu(self):
            return {
                'type': 'ir.actions.act_window',
                'name': 'Reports',
                'view_mode': 'tree',
                'res_model': 'sale.report',
                'target': 'current',
            }


    def open_tasks_menu(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Tasks',
            'view_mode': 'tree',
            'res_model': 'sale.order',
            'domain': [('state', '=', 'sent')],
            'target': 'current',
        }

    def open_purchase_reports(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Purchase Reports',
            'view_mode': 'tree',
            'res_model': 'purchase.report',
            'target': 'current',
        }

    def open_inventory_reports(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Inventory Reports',
            'view_mode': 'tree',
            'res_model': 'stock.report',
            'target': 'current',
        }

    # def open_accounting_menu(self):
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Accounting',
    #         'view_mode': 'tree',
    #         'res_model': 'account.move',
    #         'target': 'current',
    #     }
    def open_accounting_menu(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Dynamic Accounting Reports',
            'res_model': 'account.report',
            'view_mode': 'tree,form',
            'domain': [],
            'context': self.env.context,
            'target': 'current',
            'res_id': self.env.ref('accounting_drill_down_report.menu_accounting_dynamic_report').id,
        }
