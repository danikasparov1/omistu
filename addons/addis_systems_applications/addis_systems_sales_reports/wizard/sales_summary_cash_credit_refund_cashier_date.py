from odoo import fields, models, api, _
class SalesSummaryReportBySummariesedCashCreditRefund(models.TransientModel):
    _name = 'sales.summary.report.cash.credit.cashier.date'
    _discription="summary of cash credit refund by date and cashier"

    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    user_id = fields.Many2one('res.users',string="Cashier")
    customer_id = fields.Many2one('res.partner')
    invoice_id = fields.One2many('account.move', string="Sales Order", compute='_invoice_sales_order_compute')
    journal=fields.Many2one( 'account.journal',string="Payment Method",domain="[('type', 'in', ('bank','cash'))]")
    payment_status = fields.Selection(
            string='Payment Status',
            selection=[
                ('not_paid', 'Not Paid'),
                ('in_payment', 'In Payment'),
                ('paid', 'Paid'),
                ('partial', 'Partially Paid'),
                ('reversed', 'Reversed'),
                ('invoicing_legacy', 'Invoicing App Legacy'),
                ]
            )
    status=fields.Selection(
                string='Status',
                selection=[
                    ('posted', 'Posted'),
                    ('cancel', 'Cancelled'),
                ],
                )

    def cashiers_detail(self,cashier,moves):
        data={
                "cashsales":0,
                "creditsales":0,
                "salesrefund":0,
            }
        moves=self.env['account.move'].search([('invoice_user_id','=',cashier.id),('id','in',moves.ids)])
        for acct_move in moves:
            if acct_move.invoice_date == acct_move.invoice_date_due:
                b="cashsales"
            else:
                b="creditsales"
            data[b]+=acct_move.amount_total_signed
            if acct_move.reversal_move_id:
                data['salesrefund']+=abs(acct_move.reversal_move_id.amount_total_signed)
                data[b]-=abs(acct_move.reversal_move_id.amount_total_signed)
            
        return {"result":data}

    def get_dates(self):
        returndata={
            "date_start":'',
            "date_end":'',
            "cashiers":[],
            "moves":''
        }
        dates=set()
        cashiers=set()
        domain=['&',('move_type','=','out_invoice'),('state','!=','draft')]
        if self.date_from:
            domain += [('date', '>=', self.date_from)]
            dates.add(self.date_from)
        if self.date_to:
            domain += [('date', '<=', self.date_to)]
            dates.add(self.date_to)
        if self.journal:
            move_ids=self.env['account.payment'].search([('journal_id','=',self.journal.id)]).reconciled_invoice_ids.ids
            domain+=[('id','in',move_ids)]
        if self.status:
            domain += [('state', '=', self.status)]
        if self.payment_status:
            domain+=[('payment_state','=',self.payment_status)]    
        if self.customer_id:
            domain += [('partner_id', '=', self.customer_id.id)]
        if self.user_id:
            domain+=[('create_uid', '=', self.user_id.id)]
        acct_moves=self.env["account.move"].search(domain)
        for move in acct_moves:
            if move.invoice_date and move.invoice_user_id:
                dates.add(move.invoice_date)
            if move.invoice_user_id:
                cashiers.add(move.invoice_user_id)
        returndata["date_start"]=min(dates) if dates else []
        returndata["date_end"]=max(dates) if dates else []
        returndata['cashiers']=cashiers
        returndata['moves']=acct_moves
        return {"result":returndata}
    def generate_report(self):
        return self.env.ref('addis_systems_sales_reports.addis_sales_summary_report_cash_credit_cashier').report_action(self)


