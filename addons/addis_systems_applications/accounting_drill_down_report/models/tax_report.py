import calendar
import io
import json
from datetime import datetime
import xlsxwriter
from odoo import models, fields, api
from odoo.tools.date_utils import get_month, get_fiscal_year, \
    get_quarter_number, subtract





class ReportTax(models.AbstractModel):
    _name = 'addissystems.report_tax'
    _description = 'Tax Report'

    def _sql_from_amls_one(self):
        sql = """SELECT "account_move_line".tax_line_id, COALESCE(SUM("account_move_line".debit-"account_move_line".credit), 0)
                    FROM %s
                    WHERE %s GROUP BY "account_move_line".tax_line_id"""
        return sql

    def _sql_from_amls_two(self):
        sql = """SELECT r.account_tax_id, COALESCE(SUM("account_move_line".debit-"account_move_line".credit), 0)
                 FROM %s
                 INNER JOIN account_move_line_account_tax_rel r ON ("account_move_line".id = r.account_move_line_id)
                 INNER JOIN account_tax t ON (r.account_tax_id = t.id)
                 WHERE %s GROUP BY r.account_tax_id"""
        return sql

    def _compute_from_amls(self, options, taxes):
        #compute the tax amount
        sql = self._sql_from_amls_one()
        tables, where_clause, where_params = self.env['account.move.line']._addissystems_query_get()
        query = sql % (tables, where_clause)
        self.env.cr.execute(query, where_params)
        results = self.env.cr.fetchall()
        for result in results:
            if result[0] in taxes:
                taxes[result[0]]['tax'] = abs(result[1])

        #compute the net amount
        sql2 = self._sql_from_amls_two()
        query = sql2 % (tables, where_clause)
        self.env.cr.execute(query, where_params)
        results = self.env.cr.fetchall()
        for result in results:
            if result[0] in taxes:
                taxes[result[0]]['net'] = abs(result[1])

    @api.model
    def get_lines(self, options):
        taxes = {}
        for tax in self.env['account.tax'].search([('type_tax_use', '!=', 'none')]):
            if tax.children_tax_ids:
                for child in tax.children_tax_ids:
                    if child.type_tax_use != 'none':
                        continue
                    taxes[child.id] = {'tax_id':child.id,'tax': 0, 'net': 0, 'name': child.name, 'type': tax.type_tax_use}
            else:
                taxes[tax.id] = {'tax_id':tax.id,'tax': 0, 'net': 0, 'name': tax.name, 'type': tax.type_tax_use}
        self.with_context(date_from=options['date_from'], date_to=options['date_to'],
                          state=options['target_move'],
                          strict_range=True)._compute_from_amls(options, taxes)
        groups = dict((tp, []) for tp in ['sale', 'purchase'])
        for tax in taxes.values():
            if tax['tax']:
                groups[tax['type']].append(tax)
        return groups
    
class TaxExcelReport(models.AbstractModel):
    _name="report.accounting_drill_down_report.report_tax_xlsx"
    _inherit = 'report.report_xlsx.abstract'
    def generate_xlsx_report(self, workbook, data, partners):
        report_name="Tax Report"
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
        sheet.set_column('A:C', 30)
        index=0

        headings = workbook.add_format({'font_size': '16px', 'align': 'center', 'bold': True, 'font_color': '#000000', 'bg_color': '#F1EEEE'})
        sheet.merge_range('A1:C1', str(self.env.company.name), headings)

        # Write the report title
        sheet.merge_range('A2:C2',report_name, headings)
        index=2
        sheet.write(index,0,"Sale",main_topic_format)
        sheet.write(index,1,"Net",main_topic_format)
        sheet.write(index,2,"Tax",main_topic_format)
        index+=1
        total_sale_net=0
        total_sale_tax=0
        total_purchase_tax=0
        total_purchase_net=0
        for i,line in enumerate(data["data"]["lines"]["sale"]):
             index+=1
             sheet.write(index,0,line["name"])
             sheet.write(index,1,line["net"],number_format)
             sheet.write(index,2,line["tax"],number_format)
             total_sale_net+=line["net"]
             total_sale_tax+=line["tax"]
        index+=1
        sheet.write(index,0,"Total Sale")
        sheet.write(index,2,total_sale_tax,number_format)
        index+=1
        sheet.write(index,0,"Purchase",main_topic_format)
       
        for j,line_2 in enumerate(data["data"]['lines']['purchase']):
             index+=1
             sheet.write(index,0,line_2["name"])
             sheet.write(index,1,line_2["net"],number_format)
             sheet.write(index,2,line_2["tax"],number_format)
             total_purchase_tax +=line_2["tax"]
             total_purchase_net +=line_2["net"]
        index+=1
        sheet.write(index,0,"Total Purchase")
        sheet.write(index,2,total_purchase_tax,number_format)
                 

