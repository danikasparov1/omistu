import time
from odoo import api, models, _
from odoo.exceptions import UserError,ValidationError
from odoo.tools import date_utils
import io
import json
import xlsxwriter



class AccountAgedTrialBalanceInherited(models.TransientModel):
    _inherit = 'account.aged.trial.balance'

    def _print_report_html(self, data):
        data = self._get_report_data(data)
        return self.env.ref('addis_systems_accounting_excel_reports.action_report_aged_partner_balance_html').\
            with_context(landscape=True).report_action(self, data=data)
    def check_report_excel(self):
        data=super(AccountAgedTrialBalanceInherited,self).check_report_excel()
        data = self._get_report_data(data)
        data=self.with_context(discard_logo_check=True,active_model='account.aged.trial.balance',active_id=self.id).env["report.accounting_pdf_reports.report_agedpartnerbalance"]._get_report_values(docids=[],data=data)
        return  {
            'type': 'ir.actions.report',
            'report_type': 'excel',
            'data': {
                'model': 'account.aged.trial.balance',
                'options': json.dumps(data, default=date_utils.json_default),
                'output_format': 'xlsx',
                'report_name': f"Aged Partner Balance Report"
            }
        }

    def get_xlsx_report(self,data):
        report_name = "Aged Partner Balance"
        column_names=["Partners","Not due",data["data"]['4']['name'],data["data"]['3']['name'],data["data"]['2']['name'],data["data"]['1']['name'],data["data"]['0']['name'],"Total"]
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet(report_name[:31])
        bold = workbook.add_format({'bold': True})
        money = workbook.add_format({'num_format': 'ETB #,##0.00','align': 'right'})  # Use ETB as the currency symbol.
        main_topic_format = workbook.add_format({ 'font_size': 16})
        sheet.set_column('A:G', 30)
        headings = workbook.add_format({'font_size': '16px', 'align': 'center', 'bold': True, 'font_color': '#000000', 'bg_color': '#F1EEEE'})
        head = workbook.add_format({'font_size': '12px', 'align': 'left', 'bold': True})
        head_center = workbook.add_format({'font_size': '12px', 'align': 'center', 'bold': True})
        
        sheet.merge_range('A1:G1', str(self.env.company.name), headings)
        sheet.merge_range('A2:G2', report_name, head_center)
        for idx,name in enumerate(column_names):
            sheet.write(2,idx,name,bold)
        index=3
        if data["get_partner_lines"]:
            sheet.set_row(index, 20)
            sheet.write(index,0,"Account Total",main_topic_format)
            sheet.write(index,1,f"{data['get_direction'][6]:.2f}",money)
            sheet.write(index,2,f"{data['get_direction'][4]:.2f}",money)
            sheet.write(index,3,f"{data['get_direction'][3]:.2f}",money)
            sheet.write(index,4,f"{data['get_direction'][2]:.2f}",money)
            sheet.write(index,5,f"{data['get_direction'][1]:.2f}",money)
            sheet.write(index,6,f"{data['get_direction'][0]:.2f}",money)
            sheet.write(index,7,f"{data['get_direction'][5]:.2f}",money)
            index+=1
        for partner in data["get_partner_lines"]:
            sheet.set_row(index, 20)
            sheet.write(index,0,partner["name"],main_topic_format)
            sheet.write(index,1,f"{partner['direction']:.2f}",money)
            sheet.write(index,2,f"{partner['4']:.2f}",money)
            sheet.write(index,3,f"{partner['3']:.2f}",money)
            sheet.write(index,4,f"{partner['2']:.2f}",money)
            sheet.write(index,5,f"{partner['1']:.2f}",money)
            sheet.write(index,6,f"{partner['0']:.2f}",money)
            sheet.write(index,7,f"{partner['total']:.2f}",money)
            index+=1
        workbook.close()
        output.seek(0)
        read_output = output.read()
        output.close()
        return read_output
