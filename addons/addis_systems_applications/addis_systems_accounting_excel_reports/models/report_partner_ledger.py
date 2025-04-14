import time
from odoo import api, models, _
from odoo.exceptions import UserError,ValidationError

from odoo.tools.misc import get_lang
import io
import json
import xlsxwriter
from odoo.tools import date_utils


class AccountPartnerLedgerInherited(models.TransientModel):
     _inherit = "account.report.partner.ledger"

     def _print_report_html(self, data):
        data = self._get_report_data(data)
        return self.env.ref('addis_systems_accounting_excel_reports.action_report_partnerledger_html').with_context(landscape=True).\
            report_action(self, data=data)
     

     def check_report_excel(self):
        self.ensure_one()
        data=super(AccountPartnerLedgerInherited,self).check_report_excel()
        data = self._get_report_data(data)
        data=self.with_context(landscape=True,active_model='account.report.partner.ledger',active_id=self.id).env["report.accounting_pdf_reports.report_partnerledger"]._get_report_values(docids=[],data=data)
        data['docs']=[partner.id for partner in data['docs']]
        return  {
            'type': 'ir.actions.report',
            'report_type': 'excel',
            'data': {
                'model': 'account.report.partner.ledger',
                'options': json.dumps(data, default=date_utils.json_default),
                'output_format': 'xlsx',
                'report_name': f"{'Partner Ledger'}"
            }
        }
     
     def get_xlsx_report(self,data):
        column_names=["Date","JRNL","Account","Ref","Debit","Credit","Balance"]
        report_name = f"Partner Ledger"
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet(report_name[:31])
        bold = workbook.add_format({'bold': True})
        money = workbook.add_format({'num_format': '{self.env.user.company_id.symbol} #,##0.00','align': 'right'})  # Use ETB as the currency symbol.
        main_topic_format = workbook.add_format({ 'font_size': 16})
        main_sub_topic_format=workbook.add_format({'bold': True, 'font_size': 14,'indent': 2})
        subset_format = workbook.add_format({'italic': True, 'font_size': 12, 'indent': 4})
        sheet.set_column('A:G', 30)
        headings = workbook.add_format({'font_size': '16px', 'align': 'center', 'bold': True, 'font_color': '#000000', 'bg_color': '#F1EEEE'})
        head = workbook.add_format({'font_size': '12px', 'align': 'left', 'bold': True})
        head_center = workbook.add_format({'font_size': '12px', 'align': 'center', 'bold': True})
        
        sheet.merge_range('A1:G1', str(self.env.company.name), headings)
        sheet.merge_range('A2:G2', report_name, head_center)

        shift=0
        report_model=self.env['report.accounting_pdf_reports.report_partnerledger']
        for idx,name in enumerate(column_names):
            sheet.write(2,idx,name,bold)
        index=3
        for partner in data["docs"]:
            partner=self.env['res.partner'].browse(partner)
            sheet.set_row(index, 20)
            sheet.write(index,0,partner.name,main_topic_format)
            sheet.write(index,4,f"{report_model._sum_partner(data['data'],partner,'debit'):.2f}",money)
            sheet.write(index,5,f"{report_model._sum_partner(data['data'],partner,'credit'):.2f}",money)
            sheet.write(index,6,f"{report_model._sum_partner(data['data'],partner,'debit - credit'):.2f}",money)
            index+=1
            for j,line in enumerate(report_model._lines(data['data'], partner)):
                sheet.write(index,0,str(line["date"]),subset_format)
                sheet.write(index,1,line['code'],subset_format)
                sheet.write(index,2,line['a_code'],subset_format)
                sheet.write(index,3,line['displayed_name'],subset_format)
                sheet.write(index,4,f"{line['debit']:.2f}",money)
                sheet.write(index,5,f"{line['credit']:.2f}",money)
                sheet.write(index,6,f"{line['progress']:.2f}",money)
                index+=1

        workbook.close()
        output.seek(0)
        read_output = output.read()
        output.close()
        return read_output