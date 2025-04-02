import time
from odoo import api, models, _
from odoo.exceptions import UserError,ValidationError
from odoo.tools import date_utils
import io
import json
import xlsxwriter


class AccountPrintJournalInherited(models.TransientModel):
    _inherit = "account.print.journal"
    def _print_report_html(self, data):
        data = self._get_report_data(data)
        return self.env.ref('addis_systems_accounting_excel_reports.action_report_journal_html').with_context(landscape=True).report_action(self, data=data)

    def check_report_excel(self):
        data=super(AccountPrintJournalInherited,self).check_report_excel()
        data = self._get_report_data(data)
        data=self.with_context(discard_logo_check=True,active_model='account.print.journal',active_id=self.id).env["report.accounting_pdf_reports.report_journal"]._get_report_values(self,data)
        data["docs"]= data["docs"].ids
        data["lines"]={i:j.ids for i,j in data['lines'].items()}

        return  {
            'type': 'ir.actions.report',
            'report_type': 'excel',
            'data': {
                'model': 'account.print.journal',
                'options': json.dumps(data, default=date_utils.json_default),
                'output_format': 'xlsx',
                'report_name': f"Journals Entries"
            }
        }
    def get_xlsx_report(self, data):
        column_names=["Date","JRNL","Partner","Ref","Move","Entry Label","Debit","Credit","Balance"]
        report_name = "Journals Entries"
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
        
        sheet.merge_range('A1:G1', str(self.env.company.name), headings)
        sheet.merge_range('A2:G2', report_name, head_center)
        index=2
        double_underline_format = workbook.add_format({
            'bottom': 2,  # Double underline style
            'bottom_color': 'black'  # Color of the double underline
        })
        report_model=self.env["report.accounting_pdf_reports.report_journal"]
        for doc in data["docs"]:
            doc=self.env['account.journal'].browse(doc)
     
            sheet.write(index,0,doc.name + " Journal",double_underline_format)
            index+=1
            sheet.write(index,0,"Move",double_underline_format)
            sheet.write(index,1,"Date",double_underline_format)
            sheet.write(index,2,"Account",double_underline_format)
            sheet.write(index,3,"Partner",double_underline_format)
            sheet.write(index,4,"Label",double_underline_format)
            sheet.write(index,5,"Debit",double_underline_format)
            sheet.write(index,6,"Credit",double_underline_format)
            index+=1
            for line in data["lines"][str(doc.id)]:
                line=self.env['account.move.line'].browse(line)
                move_name=line.move_id.name != '/' and line.move_id.name or ('*'+str(line.move_id.id))
                partner_name=line.sudo().partner_id and line.sudo().partner_id.name and line.sudo().partner_id.name[:23] or ''
                label_name=(line.name and line.name[:35]) or ""
                sheet.write(index,0,move_name)
                sheet.write(index,1,str(line.date))
                sheet.write(index,2,line.account_id.code)
                sheet.write(index,3,partner_name)
                sheet.write(index,4,label_name)
                sheet.write(index,5,f"{line.debit:.2f}")
                sheet.write(index,6,f"{line.credit:.2f}")
                index+=1
            debit_total=report_model._sum_debit(data['data'],doc)
            credit_total=report_model._sum_credit(data['data'],doc)
            sheet.write(index,0,"Total",double_underline_format)
            sheet.write(index,5,f"{debit_total:.2f}",double_underline_format)
            sheet.write(index,6,f"{credit_total:.2f}",double_underline_format)
            index+=1
            sheet.write(index,0,"Name",double_underline_format)
            sheet.write(index,1,"Base Amount",double_underline_format)
            sheet.write(index,2,"Tax Amount",double_underline_format)
            index+=1
            taxes=report_model._get_taxes(data['data'], doc)
            for tax in taxes:
                sheet.write(index,0,tax.name)
                sheet.write(index,1,f"{taxes[tax]['base_amount']:.2f}")
                sheet.write(index,2,f"{taxes[tax]['tax_amount']:.2f}")
                index+=1    
        workbook.close()
        output.seek(0)
        read_output = output.read()
        output.close()
        return read_output

 