from odoo import fields, models, api, _


class SalesSummaryReportByCategory(models.TransientModel):
    _name = 'sales.summary.report.profitability'

    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    category_id = fields.Many2one('product.category')
    journal=fields.Many2one( 'account.journal',string="Payment Method",domain="[('type', 'in', ('bank','cash'))]")
    user_id = fields.Many2one('res.users',string="Cashier")
    customer_id = fields.Many2one('res.partner')
    sales_id = fields.One2many('sale.order', string="Sales Order", compute='_sales_order_compute')
    invoice_id = fields.One2many('account.move', string="Sales Order", compute='_invoice_sales_order_compute')
    order_id = fields.One2many('sale.order.line', string="Sales Order", compute='_order_sales_order_compute')
    product_id = fields.One2many('product.product', string="Sales Order", compute='_product_sales_order_compute')
    cat_id = fields.One2many('product.template', string="Sales Order", compute='_category_sales_order_compute')
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

    def return_data(self,move_lines):
        """
        "grand_parent1":{

                    "parent1":{
                            "productID1":{
                                "name":"product_name",
                                "Quantity":10,
                                "unit_price":20,
                                "Tax":90,
                                "SubTotalAmount":300,
                                "Total_Amount":0


                            },
                    }
                    }
        
        """


        mydata={
                
                    }
        for move_line in move_lines:
            
            parent=move_line.product_id.categ_id.name
            product=move_line.product_id.name
            product_id=move_line.product_id.id
            tax=move_line.price_total - move_line.price_subtotal
            qty=move_line.quantity
            sub_total_amount=move_line.price_subtotal
            total_amount=move_line.price_total
            price_unit=move_line.price_unit
            product_total_cost=move_line.product_id.standard_price * qty
            if parent in mydata:
                    mydata[parent]["Total_sale"]+=sub_total_amount
                    mydata[parent]["Total_Cost"]+=product_total_cost
                    mydata[parent]["Total_profit"]+=sub_total_amount - product_total_cost
                    

            else:
                mydata[parent]={
                                "Total_sale":sub_total_amount,
                                "Total_Cost":product_total_cost,
                                "Total_profit":sub_total_amount-product_total_cost,
                                
                                
                                }
                
        return mydata

    def check(self):
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
        account_moves=self.env['account.move'].search([('move_type', '=', 'out_invoice')]+domain)
        move_lines=self.env['account.move.line'].search([('move_id', 'in' , account_moves.ids), ('display_type', '=', 'product')])
        data=self.return_data(move_lines)
        return {"result":data}

    def generate_report_category(self):
        return self.env.ref('addis_systems_sales_reports.adis_sales_summary_report_report_profitability').report_action(self)
