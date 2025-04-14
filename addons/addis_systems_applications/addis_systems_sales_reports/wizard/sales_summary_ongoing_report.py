from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class SalesSummaryReportByCustomer(models.TransientModel):
    _name = 'sales.summary.ongoing.running'
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    user_id = fields.Many2one('res.users',string="Cashier")
    customer_id = fields.Many2one('res.partner')
    cashier_id = fields.One2many('res.users', string="Sales Order", compute='_cashier_sales_order_compute')
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
    type=fields.Selection(
                string='Type',
                default="invoice",
                selection=[
                    ('draft', 'Quotation'),
                    ('sale', 'Sales Order'),
                    ('invoice', 'Invoice'),
                ],
                )
    status=fields.Selection(
                string='Status',
                selection=[
                    ('draft', 'Draft'),
                    ('posted', 'Posted'),
                    ('cancel', 'Cancelled'),
                ],
                )
    
    def get_discount(self,move_id):
        disc=0
        movelines=self.env["account.move.line"].search([('display_type',"=","product")])
        for moveline in movelines:
            disc += moveline.quantity*moveline.price_unit*moveline.discount/100
        return disc
    def get_moves_sales(self,invoice_date):
        date_from_start = datetime.combine(invoice_date, datetime.min.time())
        date_to_end = datetime.combine(invoice_date, datetime.max.time())
        domain=[('date_order', '>=', date_from_start),('date_order', '<=', date_to_end)]
        if self.type == "sale":
            domain +=[("state","=","sale")]
        else:
            domain +=[("state","in",("draft","sent"))]
        if self.date_from:
            domain += [('date_order', '>=', self.date_from)]
        if self.date_to:
            domain += [('date_order', '<=', self.date_to)]
        if self.customer_id:
            domain += [('partner_id', '=', self.customer_id.id)]
        if self.user_id:
            domain+=[('create_uid', '=', self.user_id.id)]
        acct_moves=self.env["sale.order"].search(domain)
        return acct_moves
    

    def get_moves(self,invoice_date):
        if self.type != "invoice":
            return self.get_moves_sales(invoice_date)
        domain=[('move_type','=','out_invoice'),('invoice_date',"=",invoice_date)]
        if self.date_from:
            domain += [('date', '>=', self.date_from)]
        if self.date_to:
            domain += [('date', '<=', self.date_to)]
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
        return acct_moves

    def get_dates_sales(self):
        if self.type == "sale":
            domain=[("state","=","sale")]
        else:
            domain=[("state","in",("draft","sent"))]
        if self.date_from:
            domain += [('date_order', '>=', self.date_from)]
        if self.date_to:
            domain += [('date_order', '<=', self.date_to)]
        if self.customer_id:
            domain += [('partner_id', '=', self.customer_id.id)]
        if self.user_id:
            domain+=[('create_uid', '=', self.user_id.id)]
        acct_moves=self.env["sale.order"].search(domain)
        dates=set()
        for acctmove in acct_moves:
            if acctmove.date_order:
                dates.add(acctmove.date_order.date())
        return dates            


    def get_dates(self):
        if self.type!="invoice":
            return self.get_dates_sales()
        domain=[('move_type','=','out_invoice')]
        if self.date_from:
            domain += [('date', '>=', self.date_from)]
        if self.date_to:
            domain += [('date', '<=', self.date_to)]
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
        dates=set()
        for acctmove in acct_moves:
            if acctmove.invoice_date:
                dates.add(acctmove.invoice_date)
     
        return dates

    def generate_report(self):
        return self.env.ref('addis_systems_sales_reports.addis_sales_summary_ongoing_running').report_action(self)