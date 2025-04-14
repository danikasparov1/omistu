import io
import json
from datetime import datetime
import time
import xlsxwriter

from odoo import models, fields, api,_
from odoo.tools.date_utils import get_month, get_fiscal_year,get_quarter_number, subtract
from odoo.exceptions import UserError

class ReportBankBook(models.AbstractModel):
    _name = 'addissystems.report_bankbook'
    _description = 'Bank Book  Report'
    @api.model
    def get_default_account_ids(self):
        journals = self.env['account.journal'].search([('type', '=', 'bank')])
        accounts = []
        for journal in journals:
            if journal.default_account_id.id:
                accounts.append(journal.default_account_id.id)
            if journal.company_id.account_journal_payment_credit_account_id.id:
                accounts.append(journal.company_id.account_journal_payment_credit_account_id.id)
            if journal.company_id.account_journal_payment_debit_account_id.id:
                accounts.append(journal.company_id.account_journal_payment_debit_account_id.id)
            for acc_out in journal.outbound_payment_method_line_ids:
                if acc_out.payment_account_id:
                    accounts.append(acc_out.payment_account_id.id)
            for acc_in in journal.inbound_payment_method_line_ids:
                if acc_in.payment_account_id:
                    accounts.append(acc_in.payment_account_id.id)
        accounts = list(set(accounts))
        account_records = self.env["account.account"].browse(accounts)
        export_data = [{"id": rec.id, "code": rec.code, "name": rec.name} for rec in account_records]
        return export_data
    
    @api.model
    def sql_query(self,line_ids=[]):
        query = """
    SELECT 
        aml.account_id, 
        aa.code,
        aa.name,
        COALESCE(SUM(aml.debit), 0) AS Debit, 
        COALESCE(SUM(aml.credit), 0) AS Credit,
        COALESCE(SUM(aml.balance), 0) AS Balance
    FROM 
        account_move_line aml
    JOIN 
        account_account aa 
    ON 
        aml.account_id = aa.id
    WHERE 
        aml.id IN %s 
        AND aml.display_type NOT IN ('line_section', 'line_note')
        AND aml.parent_state != 'cancel'
    GROUP BY 
        aml.account_id, aa.code, aa.name;
"""
        self.env.cr.execute(query,[line_ids])
        results = self.env.cr.fetchall()
        return results


    
    
    @api.model
    def get_constant_domain(self,form_data):
        domain=[('display_type', 'not in', ('line_section', 'line_note')),('parent_state','!=','cancel')]
        jrnls=[jrnl.get("id") for jrnl in form_data.get("journals") if jrnl.get("selected")] or [jrnl.get("id") for jrnl in form_data.get("journals")]
        account_ids=[acct["id"] for acct in self.get_default_account_ids()]
        if form_data.get("accounts",False):
            account_ids = [acct.get("id") for acct in form_data.get("accounts") if acct.get("selected")] or account_ids
        if form_data.get("date_from"):
            domain+=[("date",">=",form_data.get("date_from"))]
        if form_data.get("date_to"):
            domain+=[("date","<=",form_data.get("date_to"))]
        if form_data.get("journals"):
             domain+=[("journal_id", "in", jrnls)]
        if form_data.get("target_move")=="posted":
             domain+=[('parent_state','=',form_data.get("target_move"))]
        domain+=[('account_id','in',account_ids)]
        return domain
    @api.model
    def get_lines(self,form_data):
        data = {

        }
        domain = self.get_constant_domain(form_data)
        lines=self.env['account.move.line'].search(domain,order="date")
        if not lines.ids:
            return []
        account_data = self.sql_query(tuple(lines.ids))
        for account in account_data:
            data[account[0]]={
                "id":account[0],
                "name" : account[2].get('en_US'),
                "code" : account[1],
                "selected":False,
                "total_data":[account[3],account[4],account[5]],
                "data":[]
                
            }
            lines=self.env['account.move.line'].search(domain+[('account_id','=',account[0])],order="date")
            for line in lines :
                line_data = {
                    "id":line.move_id.id,
                    "date":line.date,
                    "journal":line.journal_id.name,
                    "partner":line.partner_id.name or ' ',
                    "move_name":line.move_id.name,
                    "debit":line.debit,
                    "credit":line.credit,
                    "balance":line.balance
                    
                    }
                data[account[0]]["data"].append(line_data)
        return data
    


class BankBookExcelReport(models.AbstractModel):
    _name="report.accounting_drill_down_report.report_bankbook_xlsx"
    _inherit = 'report.report_xlsx.abstract'
    def generate_xlsx_report(self, workbook, data, partners):
        report_name="Bank Book"
        sheet = workbook.add_worksheet(report_name[:31])
        bold = workbook.add_format({'bold': True})
        money = workbook.add_format({'num_format': 'ETB #,##0.00','align': 'right'})  # Use ETB as the currency symbol.
        main_topic_format = workbook.add_format({'bold': True, 'font_size': 16})
        main_sub_topic_format=workbook.add_format({'bold': True, 'font_size': 14,'indent': 2})
        subset_format = workbook.add_format({'italic': True, 'font_size': 12, 'indent': 4})
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#D3D3D3',
            'border': 1
        })
        number_format = workbook.add_format({
            'font_size': 10,
            'border': 1,
            'align': 'right',
            'num_format': '0.00'  # Ensures numbers are formatted with two decimal places
        })
        sheet.set_column('A:G', 30)
        index=0

        headings = workbook.add_format({'font_size': '16px', 'align': 'center', 'bold': True, 'font_color': '#000000', 'bg_color': '#F1EEEE'})
        sheet.merge_range('A1:G1', str(self.env.company.name), headings)

        # Write the report title
        sheet.merge_range('A2:G2',report_name, headings)
        index=2
        headers = ["Date","JRNL", "Partner","Move","Debit", "Credit", "Balance"]
        for col, header in enumerate(headers):
            sheet.write(index, col, header, header_format)
        for i,line in enumerate(data["data"]["lines"]):
             index+=1
             sheet.write(index,0,data["data"]["lines"][line]["code"] + " " + data["data"]["lines"][line]["name"],main_topic_format)
             sheet.write(index,4,data["data"]["lines"][line]["total_data"][0],number_format)
             sheet.write(index,5,data["data"]["lines"][line]["total_data"][1],number_format)
             sheet.write(index,6,data["data"]["lines"][line]["total_data"][2],number_format)
             for j,line_2 in enumerate(data["data"]['lines'][line]['data']):
                 index+=1
                 sheet.write(index,0,line_2['date'])
                 sheet.write(index,1,line_2['journal'])
                 sheet.write(index,2,line_2['partner'])
                 sheet.write(index,3,line_2['move_name'])
                 sheet.write(index,4,line_2['debit'],number_format)
                 sheet.write(index,5,line_2['credit'],number_format)
                 sheet.write(index,6,line_2['balance'],number_format)
                 