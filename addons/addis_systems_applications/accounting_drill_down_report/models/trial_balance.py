import time
from odoo import api, models, _
from odoo.exceptions import UserError

class ReportTrialBalance(models.AbstractModel):
    _name = 'addissystems.report_trialbalance'
    _description = 'Trial balance Report'


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
        jrnls=[jrnl.get("id") for jrnl in form_data.get("journals") if jrnl.get("selected")] or [jrnl.get("id") for jrnl in form_data.get("journals")]
        domain=[]
        if form_data.get("date_from"):
            domain+=[("date",">=",form_data.get("date_from"))]
        if form_data.get("date_to"):
            domain+=[("date","<=",form_data.get("date_to"))]
        if form_data.get("journals"):
             domain+=[("journal_id", "in", jrnls)]
        if form_data.get("target_move")=="posted":
             domain+=[('parent_state','=',form_data.get("target_move"))]
        return domain
    
    @api.model
    def get_lines(self,form_data):
        data={
        }
        domain = self.get_constant_domain(form_data)
        lines=self.env['account.move.line'].search(domain)
        if lines.ids:
            accounts=self.sql_query(tuple(lines.ids))
            for acct in accounts:
                data[acct[0]]={
                    "data_lines":[],
                    "label":acct[1]+" "+acct[2].get('en_US'),
                    "debit":acct[3],
                    "credit":acct[4],
                    "balance":acct[5],
                    "selected":False,
                }
        return data





class TrialBalanceExcelReport(models.AbstractModel):
    _name="report.accounting_drill_down_report.report_trialbalance_xlsx"
    _inherit = 'report.report_xlsx.abstract'
    def generate_xlsx_report(self, workbook, data, partners):
        report_name="Trial Balance"
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
        sheet.set_column('A:D', 30)
        index=0

        headings = workbook.add_format({'font_size': '16px', 'align': 'center', 'bold': True, 'font_color': '#000000', 'bg_color': '#F1EEEE'})
        sheet.merge_range('A1:D1', str(self.env.company.name), headings)

        # Write the report title
        sheet.merge_range('A2:D2',report_name, headings)
        index=2
        headers = ["Account","Debit", "Credit", "Balance"]
        for col, header in enumerate(headers):
            sheet.write(index, col, header, header_format)
        for i,line in enumerate(data["data"]["lines"]):
             index+=1
             sheet.write(index,0,data["data"]["lines"][line]["label"])
             sheet.write(index,1,data["data"]["lines"][line]["debit"],number_format)
             sheet.write(index,2,data["data"]["lines"][line]["credit"],number_format)
             sheet.write(index,3,data["data"]["lines"][line]["balance"],number_format)
                 