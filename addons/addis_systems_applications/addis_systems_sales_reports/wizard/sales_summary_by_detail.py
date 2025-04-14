from odoo import fields, models, api, _


class SalesSummaryReportByDetail(models.TransientModel):
    _name = 'sales.summary.report.detail'

    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    customer_id = fields.Many2one('res.partner')
    invoices_id = fields.Many2one('account.move',domain="[('move_type', '=', 'out_invoice')]")
    user_id = fields.Many2one('res.users',string="Cashier")
    sales_id = fields.One2many('sale.order', string="Sales Order", compute='_sales_order_compute')
    partner_id = fields.One2many('res.partner', string="Sales Order", compute='_customer_sales_order_compute')
    product_id = fields.One2many('product.product', string="Sales Order", compute='_product_sales_order_compute')
    invoice_id = fields.One2many('account.move', string="Sales Order", compute='_invoice_sales_order_compute',domain="[('move_type', '=', 'out_invoice')]")
    order_id = fields.One2many('sale.order.line', string="Sales Order", compute='_order_sales_order_compute')
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
    type=fields.Selection(
                string='Type',
                default="invoice",
                selection=[
                    ('draft', 'Quotation'),
                    ('sale', 'Sales Order'),
                    ('invoice', 'Invoice'),
                ],
                )
    @api.depends('date_from', 'date_to', 'invoices_id')
    def _sales_order_compute(self):
        domain = []
        invoices_id = self.invoices_id
        if invoices_id:
            domain += [('id', '=', invoices_id.id)]
        
        self.sales_id = self.env['sale.order'].search(domain)
        self.partner_id = self.env['res.partner'].search(domain)

        a = self.env['sale.order'].search(domain)
        b = self.env['res.partner'].search(domain)

        return a.ids, b.ids
        
    def _customer_sales_order_compute(self):
        domain = []
        
        self.partner_id = self.env['res.partner'].search(domain)

        b = self.env['res.partner'].search(domain)

        return b.ids
    
    def _product_sales_order_compute(self):
        domain = []
        
        self.product_id = self.env['product.product'].search(domain)

        c = self.env['product.product'].search(domain)

        return c.ids
    
    def _invoice_sales_order_compute(self):
        domain = []
        
        self.invoice_id = self.env['account.move'].search(domain)

        d = self.env['account.move'].search(domain)

        return d.ids
    
    def _order_sales_order_compute(self):
        domain = []
        
        self.order_id = self.env['sale.order.line'].search(domain)

        e = self.env['sale.order.line'].search(domain)

        return e.ids
    
    def test_one_sales(self, invoice, date_from, date_to):
        domain = []
        if invoice:
            domain += [('id', '=', invoice.id)]
        if date_from:
            domain += [('date_order', '>=', date_from)]
        if date_to:
            domain += [('date_order', '<=', date_to)]
        return  self.env['sale.order'].search(domain)


    def test_one(self, invoice, date_from, date_to):
        if self.type!="invoice":
            return self.test_one_sales(invoice,date_from,date_to)
        domain = []
        if invoice:
            domain += [('id', '=', invoice.id)]
        if date_from:
            domain += [('date', '>=', date_from)]
        if date_to:
            domain += [('date', '<=', date_to)]

        domain += [('move_type', '=', 'out_invoice')]
        return  self.env['account.move'].search(domain)
    
    
    def test_two_sales(self, order):
        return self.env['sale.order.line'].search([('order_id', '=' , order.id)])
    


    def test_two(self, invoice):
        if self.type!="invoice":
            return self.test_two_sales(invoice)
        return  self.env['account.move.line'].search([('move_id', '=', invoice.id), ('display_type', '=', 'product')])
        
    
    def test_three_sales(self, invoice):
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
        return self.env['sale.order'].search(domain)
    
    def test_three(self, invoice):
        if self.type!="invoice":
            return self.test_three_sales(invoice)
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
        domain +=[('move_type', '=', 'out_invoice')]
        
        invoice_user = []
        if invoice:
            domain += [('id', '=', invoice.id)]
        return self.env['account.move'].search(domain)
        
    
    def generate_report_detail(self):
        return self.env.ref('addis_systems_sales_reports.addis_sales_summary_report_report_detail').report_action(self)