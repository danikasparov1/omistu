import time
from odoo import api, models, _
from odoo.exceptions import UserError,ValidationError
from odoo.tools import date_utils
import io
import json
import xlsxwriter

class AccountBalanceReportInherited(models.TransientModel):
    _inherit = 'account.balance.report'

    def _print_report_html(self, data):
        records, data = self._get_report_data(data)
        return self.env.ref('addis_systems_accounting_excel_reports.action_report_trial_balance_html').report_action(records, data=data)
    def check_report_excel(self):
        data=super(AccountBalanceReportInherited,self).check_report_excel()
        records, data = self._get_report_data(data)
        data=self.with_context(discard_logo_check=True,active_model='account.balance.report',active_id=self.id).env["report.accounting_pdf_reports.report_trialbalance"]._get_report_values(records,data)
        return  {
            'type': 'ir.actions.report',
            'report_type': 'excel',
            'data': {
                'model': 'account.balance.report',
                'options': json.dumps(data, default=date_utils.json_default),
                'output_format': 'xlsx',
                'report_name': f"Trial Balance"
            }
        }
    def get_xlsx_report(self, data):
        column_names=["Code","Account","Debit","Credit","Balance"]
        report_name = "Trial Balance"
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet(report_name[:31])
        bold = workbook.add_format({'bold': True})
        money = workbook.add_format({'num_format': 'ETB #,##0.00','align': 'right'})  # Use ETB as the currency symbol.
        main_topic_format = workbook.add_format({ 'font_size': 16})
        subset_format = workbook.add_format({'italic': True, 'font_size': 12, 'indent': 4})
        sheet.set_column('A:G', 30)
        headings = workbook.add_format({'font_size': '16px', 'align': 'center', 'bold': True, 'font_color': '#000000', 'bg_color': '#F1EEEE'})
        head = workbook.add_format({'font_size': '12px', 'align': 'left', 'bold': True})
        head_center = workbook.add_format({'font_size': '12px', 'align': 'center', 'bold': True})
        
        sheet.merge_range('A1:E1', str(self.env.company.name), headings)
        sheet.merge_range('A2:E2', report_name, head_center)
        for idx,name in enumerate(column_names):
            sheet.write(2,idx,name,bold)
        index=3
        for account in data["Accounts"]:
            sheet.set_row(index, 20)
            sheet.write(index,0,account["code"],main_topic_format)
            sheet.write(index,1,account['name'])
            sheet.write(index,2,f"{account['debit']:.2f}",money)
            sheet.write(index,3,f"{account['credit']:.2f}",money)
            sheet.write(index,4,f"{account['balance']:.2f}",money)
            index+=1
        workbook.close()
        output.seek(0)
        read_output = output.read()
        output.close()
        return read_output


class ReportTrialBalanceExcel(models.AbstractModel):
    _name = 'report.accounting_pdf_reports.report_trialbalance_excel'
    _inherit = 'report.report_xlsx.abstract'
    def filtercolumn(self,main_column=["Date","JRNL","Ref","Debit","Credit","Balance"],data_column=[]):
        return [column for column in main_column if column in data_column ]
    
    def generate_xlsx_report(self,workbook, data, partners):
        data_model=self.env["report.accounting_pdf_reports.report_trialbalance"]
        returned_data=data_model._get_report_values(docids=[],data=data)
        column_names=["Code","Account","Debit","Credit","Balance"]
        report_name = "Partner Ledger"
        sheet = workbook.add_worksheet(report_name[:31])
        bold = workbook.add_format({'bold': True})
        money = workbook.add_format({'num_format': 'ETB #,##0.00','align': 'right'})  # Use ETB as the currency symbol.
        main_topic_format = workbook.add_format({ 'font_size': 16})
        subset_format = workbook.add_format({'italic': True, 'font_size': 12, 'indent': 4})
        sheet.set_column('A:G', 30)
        for idx,name in enumerate(column_names):
            sheet.write(0,idx,name,bold)
        index=1
        for account in returned_data["Accounts"]:
            sheet.set_row(index, 20)
            sheet.write(index,0,account["code"],main_topic_format)
            sheet.write(index,1,account['name'])
            sheet.write(index,2,f"{account['debit']:.2f}",money)
            sheet.write(index,3,f"{account['credit']:.2f}",money)
            sheet.write(index,4,f"{account['balance']:.2f}",money)
            index+=1
    