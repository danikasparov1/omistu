from odoo import fields, models, api, _

class SalesSummaryReportCashCreditRefund(models.TransientModel):
    _name = 'sales.report.cash.credit.refund'
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
                    ('draft', 'Draft'),
                    ('posted', 'Posted'),
                    ('cancel', 'Cancelled'),
                ],
                )


    def get_contents(self,product):
        data={
            "Cash":{
                "quantity":0,
                "unitprice":0,
                "total":0,
                "discount":0,
                "grand_total":0,
            },
            "Credit":{
                "quantity":0,
                "unitprice":0,
                "total":0,
                "discount":0,
                "grand_total":0,
                
            },
            "Refund":{
                "quantity":0,
                "unitprice":0,
                "total":0,
                "discount":0,
                "grand_total":0,
            }
        }

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

        for acct_move in acct_moves:
            accmovelines=self.env["account.move.line"].search([('display_type', '=', 'product'),('product_id','=',product.id),('move_id','=',acct_move.id)])
            if acct_move.invoice_date == acct_move.invoice_date_due:
                b="Cash"
            else:
                b="Credit"
            for acct_line in accmovelines:
                data[b]["quantity"]+=acct_line.quantity
                data[b]["total"]+=acct_line.price_subtotal
                data[b]['discount']+=acct_line.price_subtotal*acct_line.discount/100
                data[b]["grand_total"]+=acct_line.price_total

            if acct_move.reversal_move_id:
                 for acct_move_rev in acct_move.reversal_move_id:
                    accmovelines_ref=self.env["account.move.line"].search([('display_type', '=', 'product'),('product_id','=',product.id),('move_id','=',acct_move.reversal_move_id.id)])
                    for acct_line_ref in accmovelines_ref:
                        data[b]["quantity"]-=acct_line_ref.quantity
                        data[b]["total"]-=acct_line_ref.price_subtotal
                        data[b]['discount']-=acct_line.quantity*acct_line.price_unit*acct_line.discount/100
                        data[b]["grand_total"]-=acct_line.price_total
                        data["Refund"]["quantity"]+=acct_line_ref.quantity
                        data["Refund"]["total"]+=acct_line_ref.price_subtotal
                        data["Refund"]['discount']+=acct_line.price_subtotal*acct_line.discount/100
                        data["Refund"]["grand_total"]+=acct_line.price_total
        return data



    def get_products(self):
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
        acct_moves=self.env["account.move"].search(domain).ids
        accmovelines=self.env["account.move.line"].search([('display_type', '=', 'product'),("move_id",'in',acct_moves)])
        products=accmovelines.product_id
        return products



    def generate_report_category(self):
        return self.env.ref('addis_systems_sales_reports.addis_sales_summary_report_report_cash_credit_refund').report_action(self)
