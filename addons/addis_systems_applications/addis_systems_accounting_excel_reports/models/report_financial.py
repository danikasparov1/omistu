import time
from odoo import api, models, _
from odoo.exceptions import UserError,ValidationError
from odoo.tools.misc import get_lang
from odoo.tools import date_utils
import io
import json
import xlsxwriter

class AccountingReportExcel(models.TransientModel):
    _inherit = "accounting.report"
    def _print_report_html(self, data):
        data['form'].update(self.read(['date_from_cmp', 'debit_credit', 'date_to_cmp', 'filter_cmp', 'account_report_id', 'enable_filter', 'label_filter', 'target_move'])[0])
        return self.env.ref('addis_systems_accounting_excel_reports.action_report_financial_html').report_action(self, data=data, config=False)

    def check_report_excel(self):
        self.ensure_one()
        data_model=self.env["report.accounting_pdf_reports.report_financial"]
        data=super(AccountingReportExcel,self).check_report_excel()
        data['form'].update(self.read(['date_from_cmp', 'debit_credit', 'date_to_cmp', 'filter_cmp', 'account_report_id', 'enable_filter', 'label_filter', 'target_move'])[0])
        response_data=self.with_context(discard_logo_check=True,active_model='accounting.report',active_id=self.id).env["report.accounting_pdf_reports.report_financial"]._get_report_values(docids=[],data=data)
        return  {
            'type': 'ir.actions.report',
            'report_type': 'excel',
            'data': {
                'model': 'accounting.report',
                'options': json.dumps(response_data, default=date_utils.json_default),
                'output_format': 'xlsx',
                'report_name': f"{self.account_report_id.name}"
            }
        }

    def get_xlsx_report(self, data):
        column_names=["name"]
        if data['data']['debit_credit'] == 1:
            column_names+=["debit","credit"]
        column_names.append("balance")
        report_name =data['data']['account_report_id'][-1]
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet(report_name[:31])
        bold = workbook.add_format({'bold': True})
        money = workbook.add_format({'num_format': 'ETB #,##0.00','align': 'right'})  # Use ETB as the currency symbol.
        main_topic_format = workbook.add_format({'bold': True, 'font_size': 16})
        main_sub_topic_format=workbook.add_format({'bold': True, 'font_size': 14,'indent': 2})
        subset_format = workbook.add_format({'italic': True, 'font_size': 12, 'indent': 4})
        sheet.set_column('A:D', 30)
        shift=0
        if not "debit" in column_names:
            shift=2
        for z,da in enumerate(column_names):
            sheet.write(0,z,da,bold)
        for i,re_data in enumerate(data['get_account_lines']):
            if int(re_data['level'])==0:
                sheet.set_row(i+1, 40)
                sheet.write(i+1,0,re_data["name"],main_topic_format)
                if not shift:
                    sheet.write(i+1,1,f"{re_data['debit']:.2f}",money)
                    sheet.write(i+1,2,f"{re_data['credit']:.2f}",money)
               
                sheet.write(i+1,3-shift,f"{re_data['balance']:.2f}",money)
            elif int(re_data['level'])==2:
                sheet.set_row(i+1, 30)
                sheet.write(i+1,0,re_data["name"],main_sub_topic_format)
                if not shift:
                    sheet.write(i+1,1,f"{re_data['debit']:.2f}",money)
                    sheet.write(i+1,2,f"{re_data['credit']:.2f}",money)
                sheet.write(i+1,3-shift,f"{re_data['balance']:.2f}",money)
            else:
                sheet.write(i+1,0,re_data["name"],subset_format)
                if not shift:
                    sheet.write(i+1,1,f"{re_data['debit']:.2f}",money)
                    sheet.write(i+1,2,f"{re_data['credit']:.2f}",money)
                sheet.write(i+1,3-shift,f"{re_data['balance']:.2f}",money)
        workbook.close()
        output.seek(0)
        read_output = output.read()
        output.close()
        return read_output

class AccountCommonReportExcel(models.TransientModel):
    _inherit = "account.common.report"
    def check_report_excel(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['date_from', 'date_to', 'journal_ids', 'target_move', 'company_id'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=get_lang(self.env).code)
        return data
    
    def check_report_html(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['date_from', 'date_to', 'journal_ids', 'target_move', 'company_id'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=get_lang(self.env).code)
        return self.with_context(discard_logo_check=True)._print_report_html(data)






