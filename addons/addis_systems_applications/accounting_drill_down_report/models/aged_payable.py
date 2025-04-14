import io
import json
from datetime import datetime
import time
import xlsxwriter
from odoo.tools import float_is_zero
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api,_
from odoo.tools.date_utils import get_month, get_fiscal_year,get_quarter_number, subtract
from odoo.exceptions import UserError

class ReportAgedPayble(models.AbstractModel):
    _name = 'addissystems.report_agedpayable'
    _description = 'Aged Payable  Report'
    


    

    @api.model
    def _get_partner_move_lines(self, account_type, partner_ids,
                                date_from, target_move, period_length):
        # This method can receive the context key 'include_nullified_amount' {Boolean}
        # Do an invoice and a payment and unreconcile. The amount will be nullified
        # By default, the partner wouldn't appear in this report.
        # The context key allow it to appear
        # In case of a period_length of 30 days as of 2019-02-08, we want the following periods:
        # Name       Stop         Start
        # 1 - 30   : 2019-02-07 - 2019-01-09
        # 31 - 60  : 2019-01-08 - 2018-12-10
        # 61 - 90  : 2018-12-09 - 2018-11-10
        # 91 - 120 : 2018-11-09 - 2018-10-11
        # +120     : 2018-10-10
        periods = {}
        if not date_from:
            date_from =datetime.now().date()
        else:
            date_from=datetime.fromisoformat(date_from).date()

        start = datetime.strptime(str(date_from), "%Y-%m-%d")
        date_from = datetime.strptime(str(date_from), "%Y-%m-%d").date()
        for i in range(5)[::-1]:
            stop = start - relativedelta(days=period_length)
            period_name = str((5-(i+1)) * period_length + 1) + '-' + str((5-i) * period_length)
            period_stop = (start - relativedelta(days=1)).strftime('%Y-%m-%d')
            if i == 0:
                period_name = '+' + str(4 * period_length)
            periods[str(i)] = {
                'name': period_name,
                'stop': period_stop,
                'start': (i!=0 and stop.strftime('%Y-%m-%d') or False),
            }
            start = stop

        res = []
        total = []
        cr = self.env.cr
        user_company = self.env.user.company_id
        user_currency = user_company.currency_id
        company_ids = self._context.get('company_ids') or [user_company.id]
        move_state = ['draft', 'posted']
        date = self._context.get('date') or fields.Date.today()
        company = self.env['res.company'].browse(self._context.get('company_id')) or self.env.company

        if target_move == 'posted':
            move_state = ['posted']
        arg_list = (tuple(move_state), tuple(account_type))

        reconciliation_clause = '(l.reconciled IS FALSE)'
        cr.execute('SELECT debit_move_id, credit_move_id FROM account_partial_reconcile where max_date > %s', (date_from,))
        reconciled_after_date = []
        for row in cr.fetchall():
            reconciled_after_date += [row[0], row[1]]
        if reconciled_after_date:
            reconciliation_clause = '(l.reconciled IS FALSE OR l.id IN %s)'
            arg_list += (tuple(reconciled_after_date),)
        arg_list += (date_from, tuple(company_ids))
        query = '''
            SELECT DISTINCT l.partner_id, UPPER(res_partner.name)
            FROM account_move_line AS l left join res_partner on l.partner_id = res_partner.id, account_account, account_move am
            WHERE (l.account_id = account_account.id)
                AND (l.move_id = am.id)
                AND (am.state IN %s)
                AND (account_account.account_type IN %s)
                AND ''' + reconciliation_clause + '''
                AND (l.date <= %s)
                AND l.company_id IN %s
            ORDER BY UPPER(res_partner.name)'''
        cr.execute(query, arg_list)
        partners = cr.dictfetchall()
        # put a total of 0
        for i in range(7):
            total.append(0)

        # Build a string like (1,2,3) for easy use in SQL query
        if not partner_ids:
            partner_ids = [partner['partner_id'] for partner in partners if partner['partner_id']]
        lines = dict((partner['partner_id'] or False, []) for partner in partners)
        if not partner_ids:
            return [], [], {}

        # This dictionary will store the not due amount of all partners
        undue_amounts = {}
        query = '''SELECT l.id
                FROM account_move_line AS l, account_account, account_move am
                WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)
                    AND (am.state IN %s)
                    AND (account_account.account_type IN %s)
                    AND (COALESCE(l.date_maturity,l.date) >= %s)\
                    AND ((l.partner_id IN %s) OR (l.partner_id IS NULL))
                AND (l.date <= %s)
                AND l.company_id IN %s'''
        cr.execute(query, (tuple(move_state), tuple(account_type), date_from,
                           tuple(partner_ids), date_from, tuple(company_ids)))
        aml_ids = cr.fetchall()
        aml_ids = aml_ids and [x[0] for x in aml_ids] or []
        for line in self.env['account.move.line'].browse(aml_ids):
            partner_id = line.partner_id.id or False
            if partner_id not in undue_amounts:
                undue_amounts[partner_id] = 0.0
            line_amount = line.company_id.currency_id._convert(line.balance,
                                                               user_currency,
                                                               company, date)
            if user_currency.is_zero(line_amount):
                continue
            for partial_line in line.matched_debit_ids:
                if partial_line.max_date <= date_from:
                    line_currency = partial_line.company_id.currency_id
                    line_amount += line_currency._convert(partial_line.amount,
                                                          user_currency,
                                                          company, date)
            for partial_line in line.matched_credit_ids:
                if partial_line.max_date <= date_from:
                    line_currency = partial_line.company_id.currency_id
                    line_amount -= line_currency._convert(partial_line.amount,
                                                          user_currency,
                                                          company, date)
            if not self.env.user.company_id.currency_id.is_zero(line_amount):
                undue_amounts[partner_id] += line_amount
                lines[partner_id].append({
                    'line': line,
                    'amount': line_amount,
                    'period': 6,
                })

        # Use one query per period and store results in history (a list variable)
        # Each history will contain: history[1] = {'<partner_id>': <partner_debit-credit>}
        history = []
        for i in range(5):
            args_list = (tuple(move_state), tuple(account_type), tuple(partner_ids),)
            dates_query = '(COALESCE(l.date_maturity,l.date)'

            if periods[str(i)]['start'] and periods[str(i)]['stop']:
                dates_query += ' BETWEEN %s AND %s)'
                args_list += (periods[str(i)]['start'], periods[str(i)]['stop'])
            elif periods[str(i)]['start']:
                dates_query += ' >= %s)'
                args_list += (periods[str(i)]['start'],)
            else:
                dates_query += ' <= %s)'
                args_list += (periods[str(i)]['stop'],)
            args_list += (date_from, tuple(company_ids))

            query = '''SELECT l.id
                    FROM account_move_line AS l, account_account, account_move am
                    WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)
                        AND (am.state IN %s)
                        AND (account_account.account_type IN %s)
                        AND ((l.partner_id IN %s) OR (l.partner_id IS NULL))
                        AND ''' + dates_query + '''
                    AND (l.date <= %s)
                    AND l.company_id IN %s'''
            cr.execute(query, args_list)
            partners_amount = {}
            aml_ids = cr.fetchall()
            aml_ids = aml_ids and [x[0] for x in aml_ids] or []
            for line in self.env['account.move.line'].browse(aml_ids):
                partner_id = line.partner_id.id or False
                if partner_id not in partners_amount:
                    partners_amount[partner_id] = 0.0
                line_currency_id = line.company_id.currency_id
                line_amount = line_currency_id._convert(line.balance, user_currency, company, date)
                if user_currency.is_zero(line_amount):
                    continue
                for partial_line in line.matched_debit_ids:
                    if partial_line.max_date <= date_from:
                        line_currency_id = partial_line.company_id.currency_id
                        line_amount += line_currency_id._convert(
                            partial_line.amount, user_currency, company, date)
                for partial_line in line.matched_credit_ids:
                    if partial_line.max_date <= date_from:
                        line_currency_id = partial_line.company_id.currency_id
                        line_amount -= line_currency_id._convert(
                            partial_line.amount, user_currency, company, date)
                if not self.env.user.company_id.currency_id.is_zero(line_amount):
                    partners_amount[partner_id] += line_amount
                    lines[partner_id].append({
                        'line': line,
                        'amount': line_amount,
                        'period': i + 1,
                        })
            history.append(partners_amount)

        for partner in partners:
            if partner['partner_id'] is None:
                partner['partner_id'] = False
            at_least_one_amount = False
            values = {}
            undue_amt = 0.0
            if partner['partner_id'] in undue_amounts:  # Making sure this partner actually was found by the query
                undue_amt = undue_amounts[partner['partner_id']]

            total[6] = total[6] + undue_amt
            values['direction'] = undue_amt
            if not float_is_zero(values['direction'], precision_rounding=self.env.user.company_id.currency_id.rounding):
                at_least_one_amount = True

            for i in range(5):
                during = False
                if partner['partner_id'] in history[i]:
                    during = [history[i][partner['partner_id']]]
                # Adding counter
                total[(i)] = total[(i)] + (during and during[0] or 0)
                values[str(i)] = during and during[0] or 0.0
                if not float_is_zero(values[str(i)],
                                     precision_rounding=self.env.user.company_id.currency_id.rounding):
                    at_least_one_amount = True
            values['total'] = sum([values['direction']] + [values[str(i)] for i in range(5)])
            ## Add for total
            total[(i + 1)] += values['total']
            values['partner_id'] = partner['partner_id']
            if partner['partner_id']:
                browsed_partner = self.env['res.partner'].browse(partner['partner_id'])
                values['name'] = browsed_partner.name and len(
                    browsed_partner.name) >= 45 and browsed_partner.name[
                                                    0:40] + '...' or browsed_partner.name
                values['trust'] = browsed_partner.trust
            else:
                values['name'] = _('Unknown Partner')
                values['trust'] = False

            if at_least_one_amount or (self._context.get('include_nullified_amount') and lines[partner['partner_id']]):
                res.append(values)

        return res, total, lines
    
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
        da['form']["period_length"] = 30
        res = {}
        period_length =da['form']['period_length']
        if period_length <= 0:
            raise UserError(_('You must set a period length greater than 0.'))
        if not da['form']['date_from']:
            raise UserError(_('You must set a start date.'))
        start = da['form']['date_from']
        start = datetime.fromisoformat(start)
        for i in range(5)[::-1]:
            stop = start - relativedelta(days=period_length - 1)
            res[str(i)] = {
                'name': (i != 0 and (str((5 - (i + 1)) * period_length) + '-' + str((5 - i) * period_length)) or (
                            '+' + str(4 * period_length))),
                'stop': start.strftime('%Y-%m-%d'),
                'start': (i != 0 and stop.strftime('%Y-%m-%d') or False),
            }
            start = stop - relativedelta(days=1)
        da['form'].update(res)
        return da['form']

    @api.model
    def get_lines(self, form_data):
        form_data = self.get_domain(form_data)
        print(form_data)
        model = 'addissystems.report_agedpayable'

        target_move = form_data.get('target_move', 'all')
        date_from = form_data.get('date_from', time.strftime('%Y-%m-%d'))

        if form_data['result_selection'] == 'customer':
            account_type = ['asset_receivable']
        elif form_data['result_selection'] == 'supplier':
            account_type = ['liability_payable']
        else:
            account_type = ['asset_receivable', 'liability_payable']
        partner_ids = form_data['partner_ids']
        movelines, total, dummy = self._get_partner_move_lines(
            account_type, partner_ids, date_from, target_move, form_data.get('period_length',1)
        )
        return {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': form_data,
            'time': time,
            'get_partner_lines': movelines,
            'get_direction': total,
        }
        return ["name","herewe go"]
    
class PartnerLedgureExcelReport(models.AbstractModel):
    _name="report.accounting_drill_down_report.report_aged_payable_xlsx"
    _inherit = 'report.report_xlsx.abstract'
    def generate_xlsx_report(self, workbook, data, partners):
        report_name="Aged Partner"
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
        headers = ["Partners","Not due"]
        for i in range(4,-1,-1):
            headers.append(data['data']['lines']['data'][str(i)]['name'])
        headers.extend([
            "Account Total",
        data['data']['lines']['get_direction'][6],
        data['data']['lines']['get_direction'][4],
        data['data']['lines']['get_direction'][3],
        data['data']['lines']['get_direction'][2],
        data['data']['lines']['get_direction'][1],
        data['data']['lines']['get_direction'][0],
        data['data']['lines']['get_direction'][5]
    ])
        for col, header in enumerate(headers):
            sheet.write(index, col, header, header_format)
        for j, partner in enumerate(data['data']['lines']['get_partner_lines']):
            index += 1
            sheet.write(index, 0, partner['name'])  # Name
            sheet.write(index, 1, partner['direction'], number_format)  # Direction
            sheet.write(index, 2, partner['4'], number_format)  # Column 4
            sheet.write(index, 3, partner['3'], number_format)  # Column 3
            sheet.write(index, 4, partner['2'], number_format)  # Column 2
            sheet.write(index, 5, partner['1'], number_format)  # Column 1
            sheet.write(index, 6, partner['0'], number_format)  # Column 0
            sheet.write(index, 7, partner['total'], number_format)  # Total
