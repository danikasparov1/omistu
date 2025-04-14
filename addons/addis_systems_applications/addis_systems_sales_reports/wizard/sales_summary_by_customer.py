from odoo import fields, models, api, _


class SalesSummaryReportByUser(models.TransientModel):
    _name = 'sales.summary.report.customer'
    _description = 'Sales Summary Report View'
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
    def get_sale_lines(self,order_id=-1):
        data=self.env['sale.order.line'].search([('order_id', '=' , order_id)])
        return data
    def get_move_lines(self,move_id=-1):
        if self.type!="invoice":
            return self.get_sale_lines(order_id=move_id)
        data=self.env['account.move.line'].search([('move_id', '=' , move_id), ('display_type', '=', 'product')])
        return data

    def get_sales_person_saleorder(self):
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
        inos=self.env['sale.order'].read_group(domain=domain,fields=['partner_id'],groupby=['partner_id'],lazy=False)
        data={

        }
        for j in inos:
            domain=j.get('__domain')
            moves=self.env['sale.order'].search(domain)
            data[j.get('partner_id')]=moves
        return data        



    def get_sales_person(self):
        if self.type!="invoice":
            return self.get_sales_person_saleorder()
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
        if self.customer_id:
            domain += [('partner_id', '=', self.customer_id.id)]
        if self.user_id:
            domain+=[('create_uid', '=', self.user_id.id)]
        inos=self.env['account.move'].read_group(domain=[('move_type', '=', 'out_invoice')]+domain,fields=['invoice_partner_display_name'],groupby=['invoice_partner_display_name'],lazy=False)
        data={

        }
        for j in inos:
            domain=j.get('__domain')
            moves=self.env['account.move'].search(domain)
            data[j.get('invoice_partner_display_name')]=moves
        return data

    def generate_report_customer(self):
        return self.env.ref('addis_systems_sales_reports.addis_sales_summary_report_report_customer').report_action(self)
