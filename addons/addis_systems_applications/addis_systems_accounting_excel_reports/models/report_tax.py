import time
from odoo import api, models, _
from odoo.exceptions import UserError,ValidationError

from odoo.tools import date_utils
import io
import json
import xlsxwriter
class AccountTaxReportInherited(models.TransientModel):
    _inherit = 'account.tax.report.wizard'
    def _print_report_html(self, data):
        return self.env.ref('addis_systems_accounting_excel_reports.action_report_account_tax_html').report_action(self, data=data)

    def check_report_excel(self):
        data=super(AccountTaxReportInherited,self).check_report_excel()
        data=self.with_context(discard_logo_check=True,active_model='account.tax.report.wizard',active_id=self.id).env["report.accounting_pdf_reports.report_tax"]._get_report_values(self,data)
        return  {
            'type': 'ir.actions.report',
            'report_type': 'excel',
            'data': {
                'model': 'account.tax.report.wizard',
                'options': json.dumps(data, default=date_utils.json_default),
                'output_format': 'xlsx',
                'report_name': f"Tax Report"
            }
        }
    def get_xlsx_report(self,data):
        column_names=["Sale","Net","Tax"]
        report_name = "Tax Report"
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
        
        sheet.merge_range('A1:C1', str(self.env.company.name), headings)
        sheet.merge_range('A2:C2', report_name, head_center)
        for idx,name in enumerate(column_names):
            sheet.write(2,idx,name,bold)
        index=3
        for line in data["lines"]['sale']:
            sheet.set_row(index, 20)
            sheet.write(index,0,line["name"],main_topic_format)
            sheet.write(index,1,f"{line['net']:.2f}")
            sheet.write(index,2,f"{line['tax']:.2f}",money)
            index+=1
        sheet.write(index,0,"Purchase",bold)
        sheet.write(index,1,"Net",bold)
        sheet.write(index,2,"Tax",bold)
        index+=1
        for line in data["lines"]['purchase']:
            sheet.set_row(index, 20)
            sheet.write(index,0,line["name"],main_topic_format)
            sheet.write(index,1,f"{line['net']:.2f}")
            sheet.write(index,2,f"{line['tax']:.2f}",money)
            index+=1
        workbook.close()
        output.seek(0)
        read_output = output.read()
        output.close()
        return read_output