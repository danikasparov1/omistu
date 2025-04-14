from odoo import models, fields, api

class ManagerDashboard(models.Model):
    _name = 'manager.dashboard'
    _description = 'Manager Dashboard'

    def action_show_reports_approval_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reports Approval Wizard',
            'res_model': 'reports.approval.wizard',
            'view_mode': 'form',
            'target': 'new',
        }
    

    def action_show_reports_popup(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'manager_pre_dashboard.reports_popup',
        }

    def open_tasks_menu(self):
        # Placeholder for future implementation
        pass

    def open_purchase_reports(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Purchase Reports',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'domain': [('state', 'in', ['draft', 'to approve'])],
            'target': 'current',
        }

    def open_inventory_reports(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Inventory Reports',
            'view_mode': 'tree,form',
            'res_model': 'stock.quant',
            'target': 'current',
        }

    # def action_show_accounting_reports_wizard(self):
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Accounting Reports Wizard',
    #         'res_model': 'accounting.reports.wizard',
    #         'view_mode': 'form',
    #         'target': 'new',
    #     }
    def action_show_reports_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reports Wizard',
            'res_model': 'reportsnew.wizard',
            'view_mode': 'form',
            'target': 'new',
        }

    def open_tasks_menu(self):
        # Placeholder for future implementation
        pass

    def action_open_custom_form(self):
        """
        Action to open the form view of the custom reports.
        """
        return {
            'type': 'ir.actions.act_window',
            'name': 'Custom Report Form',
            'res_model': 'custom.reports',
            'view_mode': 'form',
            'target': 'new',  # This opens the form in a modal dialog.
        }


from odoo import models, fields, api

class ReportsWizard(models.TransientModel):
    _name = 'reportsnew.wizard'
    _description = 'Reports Wizard'

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

    def open_accounting_reports(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'accounting_reports_popup',
        }
    

from odoo import models, fields, api

class CustomReports(models.TransientModel):  # Use `TransientModel` if it's a temporary model.
    _name = 'custom.reports'
    _description = 'Custom Reports'

    name = fields.Char(string='Report Name')
    description = fields.Text(string='Description')
    date = fields.Date(string='Report Date', default=fields.Date.context_today)

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

    # def open_accounting_reports(self):
    #     return {
    #         'type': 'ir.actions.client',
    #         'tag': 'accounting_reports_popup',
    #     }

    def action_show_accounting_reports_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Accounting Reports Wizard',
            'res_model': 'accounting.reports.wizard',
            'view_mode': 'form',
            'target': 'new',
        }

from odoo import models, fields, api

class ReportsApprovalWizard(models.TransientModel):
    _name = 'reports.approval.wizard'
    _description = 'Reports Approval Wizard'

    def get_purchase_orders(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Purchase Orders to Approve',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'domain': [('state', 'in', ['draft', 'to approve'])],
            'target': 'current',
        }

    def get_sale_orders(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sales Orders to Approve',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'domain': [('state', 'in', ['draft', 'sent'])],
            'target': 'current',
        }

    def get_payment_orders(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Payment Orders to Approve',
            'view_mode': 'tree,form',
            'res_model': 'payment.order',
            'domain': [('state', 'in', ['draft', 'approved'])],
            'target': 'current',
        }


from odoo import models, fields, api

class AccountingReportsWizard(models.TransientModel):
    _name = 'accounting.reports.wizard'
    _description = 'Accounting Reports Wizard'

    def open_tax_report(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'tax_report_owl',
        }

    def open_balance_sheet_report(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'balance_sheet_report_owl',
        }

    def open_partner_ledger_report(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'addisystems_partner_ledgure',
        }

    def open_profit_and_loss_report(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'addisystems_proft_and_loss',
        }

    def open_bank_book_report(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'addisystems_bank_book',
        }

    def open_cash_book_report(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'addisystems_cash_book',
        }

    def open_aged_payable_report(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'addisystems_aged_payable',
        }

    def open_general_ledger_report(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'addisystems_general_ledgure',
        }

    def open_trial_balance_report(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'addisystems_trial_balance',
        }