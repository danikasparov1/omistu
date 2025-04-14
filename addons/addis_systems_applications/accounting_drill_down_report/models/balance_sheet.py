import io
import json
from datetime import datetime
import xlsxwriter

from odoo import models, fields, api
from odoo.tools.date_utils import get_month, get_fiscal_year,get_quarter_number, subtract


class ReportBalanceSheet(models.AbstractModel):
    _name = 'addissystems.report_balancesheet'
    _description = 'Balance Sheet Report'

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
    def get_lines(self,form_data):
        data={
            "ASSETS":{
                  "total_data":[0,0,0],
                  "datasets":{
                    "asset_cash":{
                        "label":"Bank and Cash Accounts",
                        "data":[],
                        "total":"Total Bank and Cash Accounts",
                        "total_data":[0,0,0],
                        "selected":False,
                    },
                    "asset_receivable":{
                        "label":"Receivable",
                        "data":[],
                        "total":"Total Receivables",
                        "total_data":[0,0,0],
                        "selected":False,
                    }
                    ,
                    "asset_current":{
                        "label":"Current Assets",
                        "data":[],
                        "total":"Total Current Assets",
                        "total_data":[0,0,0],
                        "selected":False,
                    },
                    "asset_non_current":
                    {
                        "label":"Non Current Assets",
                        "data":[],
                        "total":"Total Non Current Assets",
                        "total_data":[0,0,0],
                        "selected":False,
                    },

                    "asset_prepayments":{
                        "label":"Prepayments",
                        "data":[],
                        "total":"Total Prepayments",
                        "total_data":[0,0,0],
                        "selected":False,

                    },
                    "asset_fixed":{
                        "label":"Fixed Assets",
                        "data":[],
                        "total":"Total Fixed Assets",
                        "total_data":[0,0,0],
                        "selected":False,
                    },

           },
            },
        
        "LIABILITIES":{
                 "total_data":[0,0,0],
                  "datasets":{
               "liability_payable":{
                   "label":"Payables",
                   "data":[],
                   "total":"Total Payables",
                   "total_data":[0,0,0],
                   "selected":False,
               },
               "liability_credit_card":{
                   "label":"Credit Cards",
                   "data":[],
                   "total":"Total Credit Cards",
                   "total_data":[0,0,0],
                   "selected":False,
               },
               "liability_current":{
                   "label":"Current Liabilities",
                   "data":[],
                   "total":"Total Current Liabilities",
                   "total_data":[0,0,0],
                   "selected":False,
               },
                  "liability_non_current":{
                   "label":"Non Current Liabilities",
                   "data":[],
                   "total":"Total Non Current Liabilities",
                   "total_data":[0,0,0],
                   "selected":False,
               },
            
                  },

           },
           "EQUITY":{
               "total_data":[0,0,0],
                  "datasets":{
               "equity":{
                   "label":"Equity",
                   "data":[],
                   "total":"Total Equity",
                   "total_data":[0,0,0],
                   "selected":False,

               },
               "equity_unaffected":{
                   "label":"Current Year Earning",
                   "data":[],
                   "total":"Total Current Year Earning",
                   "total_data":[0,0,0],
                   "selected":False,
               },
           }
        }
        }
        domain = self.get_constant_domain(form_data)
        for gr in data:
            for d in data[gr]["datasets"]:
                lines=self.env['account.move.line'].search(domain+[("account_id.account_type",'=',d)])
                if lines.ids:
                    data[gr]["datasets"][d]["data"] = self.sql_query(tuple(lines.ids))
                    data[gr]["datasets"][d]["total_data"][0]=sum([k[3] for k in data[gr]["datasets"][d]["data"]])
                    data[gr]["datasets"][d]["total_data"][1]=sum([k[4] for k in data[gr]["datasets"][d]["data"]])
                    data[gr]["datasets"][d]["total_data"][2]=sum([k[5] for k in data[gr]["datasets"][d]["data"]])
                    data[gr]["total_data"][0]+=data[gr]["datasets"][d]["total_data"][0]
                    data[gr]["total_data"][1]+=data[gr]["datasets"][d]["total_data"][1]
                    data[gr]["total_data"][2]+=data[gr]["datasets"][d]["total_data"][2]
        return data
    

class BalanceSheetExcelReport(models.AbstractModel):
    _name="report.accounting_drill_down_report.report_balancesheet_xlsx"
    _inherit = 'report.report_xlsx.abstract'
    def generate_xlsx_report(self, workbook, data, partners):
        report_name="Balance Sheet"
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
        sheet.merge_range('A2:D2', "Balance Sheet", bold)
        index=2
        headers = ["Name", "Debit", "Credit", "Balance"]
        for col, header in enumerate(headers):
            sheet.write(index, col, header, header_format)
        for i,line in enumerate(data["data"]["lines"]):
             index+=1
             sheet.write(index,0,line,main_topic_format)
             sheet.write(index,1,data["data"]['lines'][line]['total_data'][0],number_format)
             sheet.write(index,2,data["data"]['lines'][line]['total_data'][1],number_format)
             sheet.write(index,3,data["data"]['lines'][line]['total_data'][2],number_format)
             for j,line_2 in enumerate(data["data"]['lines'][line]['datasets']):
                 index+=1
                 sheet.write(index,0,data["data"]['lines'][line]['datasets'][line_2]['label'],main_sub_topic_format)
                 sheet.write(index,1,data["data"]['lines'][line]['datasets'][line_2]['total_data'][0],number_format)
                 sheet.write(index,2,data["data"]['lines'][line]['datasets'][line_2]['total_data'][1],number_format)
                 sheet.write(index,3,data["data"]['lines'][line]['datasets'][line_2]['total_data'][2],number_format)
                 for k,line_3 in enumerate(data["data"]['lines'][line]['datasets'][line_2]['data']):
                     index+=1
                     sheet.write(index,0,line_3[1]+" "+line_3[2]['en_US'],subset_format)
                     sheet.write(index,1,line_3[3],number_format)
                     sheet.write(index,2,line_3[4],number_format)
                     sheet.write(index,3,line_3[5],number_format)

                     
                     


                 


        



    
