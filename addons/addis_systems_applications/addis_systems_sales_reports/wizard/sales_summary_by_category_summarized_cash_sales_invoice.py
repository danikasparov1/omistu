from odoo import fields, models, api, _


class SalesSummaryReportByCategory(models.TransientModel):
    _name = 'sales.summary.report.category.sales.cash.invoice'
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
        
    def return_data(self,move_lines):
        mydata={
                
                    }
        for move_line in move_lines:
            grand_parent=move_line.product_id.categ_id.parent_id.name
            parent=move_line.product_id.categ_id.name
            product=move_line.product_id.name
            product_code=move_line.product_id.default_code
            product_id=move_line.product_id.id
            tax=move_line.price_total - move_line.price_subtotal
            qty=move_line.quantity
            sub_total_amount=move_line.price_subtotal
            total_amount=move_line.price_total
            price_unit=move_line.price_unit
            discount=move_line.discount*qty*price_unit/100
            if not product:
                continue
            if grand_parent in mydata:
                if parent in mydata[grand_parent]:
                    if product_id in mydata[grand_parent][parent]:
                        mydata[grand_parent][parent][product_id]["name"]=product
                        mydata[grand_parent][parent][product_id]["code"]=product_code
                        mydata[grand_parent][parent][product_id]["Quantity"]+=qty
                        mydata[grand_parent][parent][product_id]["Tax"]+=tax
                        mydata[grand_parent][parent][product_id]["SubTotalAmount"]+=sub_total_amount
                        mydata[grand_parent][parent][product_id]["Total_Amount"]+=total_amount
                        mydata[grand_parent][parent][product_id]["discount"]+=discount

                    else:
                        mydata[grand_parent][parent][product_id]={
                                    "name":product,
                                    "code":product_code,
                                    "Quantity":qty,
                                    "unit_price":move_line.price_unit,
                                    "Tax":tax,
                                    "SubTotalAmount":sub_total_amount,
                                    "Total_Amount":total_amount,
                                    "discount":discount
                        }
                    
                else:
                    mydata[grand_parent][parent]={
                         product_id:{
                                "name":product,
                                "code":product_code,
                                "Quantity":qty,
                                "unit_price":move_line.price_unit,
                                "Tax":tax,
                                "SubTotalAmount":sub_total_amount,
                                "Total_Amount":total_amount,
                                "discount":discount
                        }
                    }





            else:
                mydata[grand_parent]={
                    parent:{
                        product_id:{
                                "name":product,
                                "code":product_code,
                                "Quantity":move_line.quantity,
                                "unit_price":move_line.price_unit,
                                "Tax":tax,
                                "SubTotalAmount":sub_total_amount,
                                "Total_Amount":total_amount,
                                "discount":discount,
                                
                        }
                    }
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
        move_ids=[]
        for move in account_moves:
            if move.invoice_date_due == move.invoice_date:
                move_ids.append(move.id)
        move_lines=self.env['account.move.line'].search([('move_id', 'in' , move_ids), ('display_type', '=', 'product')])
        data=self.return_data(move_lines)
        return {"result":data}


    def generate_report_category(self):
        return self.env.ref('addis_systems_sales_reports.sales_sales_summary_report_report_category_cash_invoice').report_action(self)
