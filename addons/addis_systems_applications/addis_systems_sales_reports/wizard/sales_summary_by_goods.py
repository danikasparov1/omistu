from odoo import fields, models, api, _
from odoo.exceptions import ValidationError 

class SalesSummaryReportByGoods(models.TransientModel):
    _name = 'sales.summary.report.goods'

    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    goods_id = fields.Many2one('product.template')
    user_id = fields.Many2one('res.users',string="Cashier")
    customer_id = fields.Many2one('res.partner')
    sales_id = fields.One2many('sale.order', string="Sales Order", compute='_sales_order_compute')
    invoice_id = fields.One2many('account.move', string="Sales Order", compute='_invoice_sales_order_compute',domain="[('move_type', '=', 'out_invoice')]")
    order_id = fields.One2many('sale.order.line', string="Sales Order", compute='_order_sales_order_compute')
    product_id = fields.One2many('product.product', string="Sales Order", compute='_product_sales_order_compute')
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
    
    @api.depends('date_from', 'date_to')
    def _sales_order_compute(self):
        domain = []
                
        if self.date_from:
            domain += [('date', '>=', self.date_from)]
        if self.date_to:
            domain += [('date', '<=', self.date_to)]

        self.sales_id = self.env['account.move'].search(domain)
    
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
    def test_one_sale_order(self,product, date_from, date_to):
        domain = []
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
        
        account_move_ids=self.env['sale.order'].search(domain).ids
        data=self.env['sale.order.line'].search([('product_template_id', '=', product.id),('order_id',"in",account_move_ids)])
        return  data

    
    def test_one(self, product, date_from, date_to):
        if self.type != "invoice":
            return self.test_one_sale_order(product, date_from, date_to)

        domain = [('move_type', '=', 'out_invoice')]
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
        
        account_move_ids=self.env['account.move'].search(domain).ids
        data=self.env['account.move.line'].search([('product_id', '=', product.id),('move_id',"in",account_move_ids)])
        return  data
    def test_three_sales(self,goods_id):
        domain_order = []
        if self.type == "sale":
            domain_order=[("state","=","sale")]
        else:
            domain_order=[("state","in",("draft","sent"))]
        order_ids=self.env['sale.order'].search(domain_order).ids

        domain=[]
        invoice_user = []
        if goods_id:
            domain += [('id', '=', goods_id.id)]
        else:
            for good in self.env['product.template'].search(domain):
                if self.env['sale.order.line'].search([('product_template_id', '=', good.id),('order_id','in',order_ids)]):
                    invoice_user += [good.id]

            domain += [('id', 'in', invoice_user)]
        return self.env['product.template'].search(domain)

    def test_three(self, goods_id):
        domain = []
        invoice_user = []
        if self.type != "invoice":
            return self.test_three_sales(goods_id)

        if goods_id:
            domain += [('id', '=', goods_id.id)]
        else:
            for good in self.env['product.template'].search(domain):
                if self.env['account.move.line'].search([('product_id', '=', good.id)]):
                 invoice_user += [good.id]
            domain += [('id', 'in', invoice_user)]

        return self.env['product.template'].search(domain)    


    def generate_report_goods(self):
        return self.env.ref('addis_systems_sales_reports.addis_sales_summary_report_report_goods').report_action(self)
