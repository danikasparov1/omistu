import time
from odoo import api, models, _
from odoo.exceptions import UserError

class ReportPartnerLedger(models.AbstractModel):
    _name = 'addissystems.report_partnerledgure'
    _description = 'Partner Ledger Report'

    def _lines(self, data, partner):
        full_account = []
        currency = self.env['res.currency']
        query_get_data = self.env['account.move.line'].with_context(data['form'])._addissystems_query_get()
        reconcile_clause = "" if data['form']['reconciled'] else ' AND "account_move_line".full_reconcile_id IS NULL '
        params = [partner.id, tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])] + query_get_data[2]
        query = """
            SELECT "account_move_line".id, m.id as move_id ,"account_move_line".date, j.code, acc.code as a_code, acc.name as a_name, "account_move_line".ref, m.name as move_name, "account_move_line".name, "account_move_line".debit, "account_move_line".credit, "account_move_line".amount_currency,"account_move_line".currency_id, c.symbol AS currency_code
            FROM """ + query_get_data[0] + """
            LEFT JOIN account_journal j ON ("account_move_line".journal_id = j.id)
            LEFT JOIN account_account acc ON ("account_move_line".account_id = acc.id)
            LEFT JOIN res_currency c ON ("account_move_line".currency_id=c.id)
            LEFT JOIN account_move m ON (m.id="account_move_line".move_id)
            WHERE "account_move_line".partner_id = %s
                AND m.state IN %s
                AND "account_move_line".account_id IN %s AND """ + query_get_data[1] + reconcile_clause + """
                ORDER BY "account_move_line".date"""
        self.env.cr.execute(query, tuple(params))
        res = self.env.cr.dictfetchall()
        sum = 0.0
        lang_code = self.env.context.get('lang') or 'en_US'
        lang = self.env['res.lang']
        lang_id = lang._lang_get(lang_code)
        date_format = lang_id.date_format
        for r in res:
            r['date'] = r['date']
            r['displayed_name'] = '-'.join(
                r[field_name] for field_name in ('move_name', 'ref', 'name')
                if r[field_name] not in (None, '', '/')
            )
            sum += r['debit'] - r['credit']
            r['progress'] = sum
            r['currency_id'] = currency.browse(r.get('currency_id'))
            full_account.append(r)
        return full_account

    def _sum_partner(self, data, partner, field):
        if field not in ['debit', 'credit', 'debit - credit']:
            return
        result = 0.0
        query_get_data = self.env['account.move.line'].with_context(data['form'])._addissystems_query_get()
        reconcile_clause = "" if data['form']['reconciled'] else ' AND "account_move_line".full_reconcile_id IS NULL '

        params = [partner.id, tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])] + query_get_data[2]
        query = """SELECT sum(""" + field + """)
                FROM """ + query_get_data[0] + """, account_move AS m
                WHERE "account_move_line".partner_id = %s
                    AND m.id = "account_move_line".move_id
                    AND m.state IN %s
                    AND account_id IN %s
                    AND """ + query_get_data[1] + reconcile_clause
        self.env.cr.execute(query, tuple(params))

        contemp = self.env.cr.fetchone()
        if contemp is not None:
            result = contemp[0] or 0.0
        return result

    @api.model
    def _generate_data(self, data=None):
        data['computed'] = {}

        obj_partner = self.env['res.partner']
        query_get_data = self.env['account.move.line'].with_context(data['form'])._addissystems_query_get()
        data['computed']['move_state'] = ['draft', 'posted']
        if data['form'].get('target_move', 'all') == 'posted':
            data['computed']['move_state'] = ['posted']
        result_selection = data['form'].get('result_selection', 'customer')
        if result_selection == 'supplier':
            data['computed']['ACCOUNT_TYPE'] = ['liability_payable']
        elif result_selection == 'customer':
            data['computed']['ACCOUNT_TYPE'] = ['asset_receivable']
        else:
            data['computed']['ACCOUNT_TYPE'] = ['asset_receivable', 'liability_payable']

        self.env.cr.execute("""
            SELECT a.id
            FROM account_account a
            WHERE a.account_type IN %s
            AND NOT a.deprecated""", (tuple(data['computed']['ACCOUNT_TYPE']),))
        data['computed']['account_ids'] = [a for (a,) in self.env.cr.fetchall()]
        params = [tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])] + query_get_data[2]
        reconcile_clause = "" if data['form']['reconciled'] else ' AND "account_move_line".full_reconcile_id IS NULL '
        query = """
            SELECT DISTINCT "account_move_line".partner_id
            FROM """ + query_get_data[0] + """, account_account AS account, account_move AS am
            WHERE "account_move_line".partner_id IS NOT NULL
                AND "account_move_line".account_id = account.id
                AND am.id = "account_move_line".move_id
                AND am.state IN %s
                AND "account_move_line".account_id IN %s
                AND NOT account.deprecated
                AND """ + query_get_data[1] + reconcile_clause
        self.env.cr.execute(query, tuple(params))
        if data['form']['partner_ids']:
            partner_ids = data['form']['partner_ids']
        else:
            partner_ids = [res['partner_id'] for res in
                           self.env.cr.dictfetchall()]
        partners = obj_partner.browse(partner_ids)
        partners = sorted(partners, key=lambda x: (x.ref or '', x.name or ''))
      
        return {
            'doc_ids': partner_ids,
            'doc_model': self.env['res.partner'],
            'data': data,
            'docs': partners,
            'time': time,
            'lines': self._lines,
            'sum_partner': self._sum_partner,
        }
    
    def get_domain(self,form_data):
        da={"form":{

        }}
        result_selection = 'customer'
        partners=False
        if form_data.get("partners",False):
            partners = [ptnl.get("id") for ptnl in form_data.get("partners") if ptnl.get("selected")] or False
        if form_data.get("account_type",False):
            result_selection=form_data.get('account_type').get('name')
        jrnls=[jrnl.get("id") for jrnl in form_data.get("journals") if jrnl.get("selected")] or [jrnl.get("id") for jrnl in form_data.get("journals")]
        da["form"]["date_from"] = form_data.get("date_from",False)
        da["form"]["date_to"] = form_data.get("date_to",False)
        da["form"]["journal_ids"] = jrnls
        da["form"]["state"] = form_data["target_move"]
        da['form']['reconciled']=False
        da['form']["partner_ids"] =  partners
        da['form']["result_selection"] = result_selection
        return da
    
    @api.model
    def get_lines(self,form_data):
        data={

        }
        domain_data = self.get_domain(form_data=form_data)
        line_data=self._generate_data(domain_data)
        for o in line_data["docs"]:
            data[o.id]={
                "name":o.name,
                "data":[],
                "selected":False,
                "total_data":[o.ref,o.name,self._sum_partner(domain_data, o, 'debit'),self._sum_partner(domain_data, o, 'credit'),self._sum_partner(domain_data, o, 'debit - credit')]
            }
            for line in  self._lines(line_data["data"],o):
                l=[line['date'],line['code'],line['a_code'],line['move_name'],line['debit'],line['credit'],line['progress'],line['currency_id'],line["move_id"]]
                data[o.id]["data"].append(l)
        return data





class GeneralLedgureExcelReport(models.AbstractModel):
    _name="report.accounting_drill_down_report.report_partnerledgure_xlsx"
    _inherit = 'report.report_xlsx.abstract'
    def generate_xlsx_report(self, workbook, data, partners):
        report_name="Partner Ledgure"
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
        headers = ["Date","JRNL", "Account","Ref","Debit", "Credit", "Balance"]
        for col, header in enumerate(headers):
            sheet.write(index, col, header, header_format)
        for i,line in enumerate(data["data"]["lines"]):
             index+=1
             sheet.write(index,0,data["data"]["lines"][line]["name"],main_topic_format)
             sheet.write(index,4,data["data"]["lines"][line]["total_data"][2],number_format)
             sheet.write(index,5,data["data"]["lines"][line]["total_data"][2],number_format)
             sheet.write(index,6,data["data"]["lines"][line]["total_data"][2],number_format)
             for j,line_2 in enumerate(data["data"]["lines"][line]['data']):
                 index+=1
                 sheet.write(index,0,line_2[0])
                 sheet.write(index,1,line_2[1])
                 sheet.write(index,2,line_2[2])
                 sheet.write(index,3,line_2[3])
                 sheet.write(index,4,line_2[4],number_format)
                 sheet.write(index,5,line_2[5],number_format)
                 sheet.write(index,6,line_2[6],number_format)
                 