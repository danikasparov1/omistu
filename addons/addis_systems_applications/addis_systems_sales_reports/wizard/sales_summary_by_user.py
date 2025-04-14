from odoo import fields, models, api, _


class SalesSummaryReportByUser(models.TransientModel):
    _name = 'sales.summary.report.user'
    _description = 'Sales Summary Report View'

    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    user_id = fields.Many2one('res.users',string="Cashier")
    customer_id = fields.Many2one('res.partner')
    
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
    def get_move_lines(self,move_id):
        if self.type=="invoice":
            data=self.env['account.move.line'].search([('move_id', '=' , move_id), ('display_type', '=', 'product')])
        else:
            data=self.env['sale.order.line'].search([('order_id', '=' , move_id)])
        return data

    def get_sales_person_sales(self):
        if self.type == "sale":
            domain=[("state","=","sale")]
        else:
            domain=[("state","in",("draft","sent"))]
        if self.date_from:
            domain += [('date_order', '>=', self.date_from)]
        if self.date_to:
            domain += [('date_order', '<=', self.date_to)]
        if self.user_id:
            domain+=[('create_uid', '=', self.user_id.id)]
        if self.customer_id:
            domain += [('partner_id', '=', self.customer_id.id)]
        inos=self.env['sale.order'].read_group(domain=domain,fields=['user_id'],groupby=['user_id'],lazy=False)
        data={

        }

        for j in inos:
            domain=j.get('__domain')
            moves=self.env['sale.order'].search(domain)
            data[j.get('user_id')[-1]]=moves
        return data

    def get_sales_person(self):
        if self.type!="invoice":
            return self.get_sales_person_sales()
        domain=[]
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
        if self.user_id:
            domain+=[('create_uid', '=', self.user_id.id)]
        if self.customer_id:
            domain += [('partner_id', '=', self.customer_id.id)]
        inos=self.env['account.move'].read_group(domain=[('move_type', '=', 'out_invoice')]+domain,fields=['invoice_user_id'],groupby=['invoice_user_id'],lazy=False)
        data={

        }

        for j in inos:
            domain=j.get('__domain')
            moves=self.env['account.move'].search(domain)
            if j.get('invoice_user_id'):
                data[j.get('invoice_user_id')[-1]]=moves
        return data

    def generate_report_user(self):
        return self.env.ref('addis_systems_sales_reports.addis_sales_summary_report_report_user').report_action(self)
