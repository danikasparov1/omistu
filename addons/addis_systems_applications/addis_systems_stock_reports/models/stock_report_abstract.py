import time
from odoo import api, models, _
from odoo.exceptions import UserError,ValidationError
from datetime import datetime, date

class ReportPrductCustomer(models.AbstractModel):
    _name = 'report.addis_systems_stock_reports.customer_movement'
    _description = 'Addissystems Stock Customer report'
    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form') or not self.env.context.get('active_model') or not self.env.context.get('active_id'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        return {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': data['form'],
            'docs': docs,
            'time': time,
        }
    

date_range_dict={"month":"This Month","year":"This Year","first-quarter":"January - March ","second-quarter":" April - June ","third-quarter":" July - September  ","last-quarter":" October - December"}

class ReportProductExpiry(models.AbstractModel):
    _name = 'report.addis_systems_stock_reports.report_pro_excel'
    _inherit = 'report.report_xlsx.abstract'

    def generate_date_label(self,date_from=None, date_to=None):
        if date_from:
            date_from = datetime.strptime(date_from, "%Y-%m-%d").strftime("%B %d, %Y")
        
        if date_to:
            date_to = datetime.strptime(date_to, "%Y-%m-%d").strftime("%B %d, %Y")
        if date_from and date_to:
            date_label = f"From {date_from} to {date_to}"
        elif date_from:
            date_label = f"From {date_from} onwards"
        elif date_to:
            date_label = f"Up to {date_to}"
        else:
            date_label = "No date range specified"
        
        return date_label



class ReportBinCard(models.AbstractModel):
    _name = 'report.addis_systems_stock_reports.product_bincard'
    _description = 'Addissystems Inventory Product Bin Card'
    @api.model
    def _get_report_values(self, docids, data=None):
        if not self.env.context.get('active_model') or not self.env.context.get('active_id'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        return {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': data['form'],
            'docs': docs,
            'time': time,
        }

class ReportPrductCategory(models.AbstractModel):
    _name = 'report.addis_systems_stock_reports.product_category'
    _description = 'Addissystems Inventory Product Category'
    @api.model
    def _get_report_values(self, docids, data=None):
        if not self.env.context.get('active_model') or not self.env.context.get('active_id'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        return {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': data['form'],
            'docs': docs,
            'time': time,
        }
    
class ReportPrductDate(models.AbstractModel):
    _name = 'report.addis_systems_stock_reports.product_date'
    _description = 'Stock Summary by Date'
    @api.model
    def _get_report_values(self, docids, data=None):
        if not self.env.context.get('active_model') or not self.env.context.get('active_id'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        return {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': data['form'],
            'docs': docs,
            'time': time,
        }

class ReportInvenetoryTrxnname(models.AbstractModel):
    _name = 'report.addis_systems_stock_reports.product_trxname'
    _description = 'Inventory Summary By Transaction name'
    @api.model
    def _get_report_values(self, docids, data=None):
        if not self.env.context.get('active_model') or not self.env.context.get('active_id'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        return {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': data['form'],
            'docs': docs,
            'time': time,
        }