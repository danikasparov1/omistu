from odoo import fields, models, api, _


class SalesSummaryReportByCategory(models.TransientModel):
    _name = 'sales.summary.report.category.cash.credit.refund'
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
    status=fields.Selection(
                string='Status',
                selection=[
                    ('draft', 'Draft'),
                    ('posted', 'Posted'),
                    ('cancel', 'Cancelled'),
                ],
                )
    

    def get_products(self,categ_id):
        products=self.env['account.move.line'].search([('product_id.categ_id','=',categ_id)]).product_id
        return products
    

    def getdata_content(self,product_id):
        data={
                "cash":{
                "quantity":0,
                "unit_price":0,
                "Tax":0,
                "SubTotalAmount":0,
                "Total_Amount":0,
                "discount":0,
                },

                "credit":{
               "quantity":0,
                "unit_price":0,
                "Tax":0,
                "SubTotalAmount":0,
                "Total_Amount":0,
                "discount":0,
                },

                "refund":{
                "quantity":0,
                "unit_price":0,
                "Tax":0,
                "SubTotalAmount":0,
                "Total_Amount":0,
                "discount":0,
                },

         }
        lines=self.env['account.move.line'].search([('product_id','=',product_id.id),('display_type','=','product')])
        for line in lines:
            move=line.move_id
            state="credit"
            if move.invoice_date == move.invoice_date_due:
                state="cash"
            type=move.move_type
            
            if type=="out_refund":
                if not move.reversed_entry_id:
                    continue
                data['refund']["quantity"]+=line.quantity
                data['refund']["unit_price"]=line.price_unit
                data['refund']["SubTotalAmount"]+=line.price_subtotal
                data['refund']["Total_Amount"]+=line.price_total
                data['refund']['discount']+=line.discount*line.quantity*line.price_unit/100
                # not being sure 
                if move.reversed_entry_id:
                    data[state]["quantity"]-=line.quantity
                    data[state]["unit_price"]=line.price_unit
                    data[state]["SubTotalAmount"]-=line.price_subtotal
                    data[state]["Total_Amount"]-=line.price_total
                    data[state]["discount"]-=line.discount*line.quantity*line.price_unit/100

        
            else:
                data[state]["quantity"]+=line.quantity
                data[state]["unit_price"]=line.price_unit
                data[state]["SubTotalAmount"]+=line.price_subtotal
                data[state]["Total_Amount"]+=line.price_total
                data[state]['discount']+=line.discount*line.quantity*line.price_unit/100

       
        return data
                
    def get_categories(self,moves):

        move_lines=self.env['account.move.line'].search([('move_id', 'in' , moves.ids), ('display_type', '=', 'product')])
        categories=set()
       
        for move_line in move_lines:
            categories.add(move_line.product_id.categ_id)
  
        return categories






                 



      



    def check(self,move_type=['out_invoice','out_refund']):
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
        account_moves=self.env['account.move'].search([('move_type', 'in', move_type)]+domain)
        move_lines=self.env['account.move.line'].search([('move_id', 'in' , account_moves.ids), ('display_type', '=', 'product')])
        data=self.get_categories(account_moves)
        return data


    def generate_report_category(self):
        return self.env.ref('addis_systems_sales_reports.sales_summary_report_category_cash_credit_refund').report_action(self)
