from odoo import fields, models, api, _
from datetime import datetime, timedelta


class SalesSummaryReportByCategory(models.TransientModel):
    _name = 'sales.summary.report.customer.type'
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
    def filter_data_sales(self):
        domain=[('date_order','!=',False)]
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
        account_moves=self.env['sale.order'].search(domain)
        return account_moves    
 

    def filter_data(self):
        if self.type!="invoice":
            return self.filter_data_sales()
        domain=[('invoice_date','!=',False)]
        if self.date_from:
            domain += [('invoice_date', '>=', self.date_from)]
        if self.date_to:
            domain += [('invoice_date', '<=', self.date_to)]
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
        return account_moves
    def get_dates_sales(self):
        dates=set()
        account_moves=self.filter_data()
        for move in account_moves:
             dates.add(move.date_order.date())
        return dates
                
    def get_dates(self):
        if self.type!="invoice":
            return self.get_dates_sales()
        dates=set()
        account_moves=self.filter_data()
        for move in account_moves:
             dates.add(move.invoice_date)
        return dates
    def get_partner_categories_sales(self,date):
        domain=[('id','in',self.filter_data().ids)]
        if self.type == "sale":
            domain +=[("state","=","sale")]
        else:
            domain +=[("state","in",("draft","sent"))]
        date_from_start = datetime.combine(date, datetime.min.time())
        date_to_end = datetime.combine(date, datetime.max.time())
        domain +=[('date_order', '>=', date_from_start),('date_order', '<=', date_to_end)]

        categs=set()
        account_moves=self.env['sale.order'].search(domain)
        for move in account_moves:
            for cat in move.partner_id.category_id:
                categs.add(cat)
        return categs

    def get_partner_categories(self,date):
        if self.type!="invoice":
            return self.get_partner_categories_sales(date)
        domain=[('invoice_date','=',date),('id','in',self.filter_data().ids)]
        categs=set()
        account_moves=self.env['account.move'].search(domain)
        for move in account_moves:
            for cat in move.partner_id.category_id:
                categs.add(cat)
        return categs
    
    def get_product_categories_sales(self,date,customer_categ):
        product_categs=set()
        date_from_start = datetime.combine(date, datetime.min.time())
        date_to_end = datetime.combine(date, datetime.max.time())
        domain=[('date_order', '>=', date_from_start),('date_order', '<=', date_to_end)]
        domain+=[('partner_id.category_id','=',customer_categ.id),('id','in',self.filter_data().ids)]
        if self.type == "sale":
            domain +=[("state","=","sale")]
        else:
            domain +=[("state","in",("draft","sent"))]
        moves=self.env['sale.order'].search(domain)
        products=self.env['sale.order.line'].search([('order_id','in',moves.ids)]).product_template_id
        for product in products:
            product_categs.add(product.categ_id)
        
        return product_categs


    def get_product_categories(self,date,customer_categ):
        if self.type!="invoice":
            return self.get_product_categories_sales(date,customer_categ)
        product_categs=set()
        domain=[('partner_id.category_id','=',customer_categ.id),('invoice_date','=',date),('id','in',self.filter_data().ids)]
        moves=self.env['account.move'].search(domain)
        products=self.env['account.move.line'].search([('display_type','=','product'),('move_id','in',moves.ids)]).product_id
        for product in products:
            product_categs.add(product.categ_id)
        
        return product_categs
    
    def pro_category_detail_sales(self,date,customer_categ,pro_categ):
        date_from_start = datetime.combine(date, datetime.min.time())
        date_to_end = datetime.combine(date, datetime.max.time())
        domain=[('date_order', '>=', date_from_start),('date_order', '<=', date_to_end)]
        if self.type == "sale":
            domain +=[("state","=","sale")]
        else:
            domain +=[("state","in",("draft","sent"))]
        data={
            "quantity":0,
            "total":0,
            "grand_total":0,
            "discount":0,
        }
        domain +=[('partner_id.category_id','=',customer_categ.id),('id','in',self.filter_data().ids)]
        moves=self.env['sale.order'].search(domain)
        
        lines=self.env['sale.order.line'].search([('order_id','in',moves.ids),('product_id.categ_id','=',pro_categ.id)])
        for line in lines:
            data['quantity']+=line.product_uom_qty
            data['total']+=line.price_subtotal
            data['grand_total']+=line.price_total
            data['discount']+=line.discount*line.price_unit*line.product_uom_qty
        
        return data


    def pro_category_detail(self,date,customer_categ,pro_categ):
        if self.type!="invoice":
            return self.pro_category_detail_sales(date,customer_categ,pro_categ)
        data={
            "quantity":0,
            "total":0,
            "grand_total":0,
            "discount":0,
        }
        
        domain=[('partner_id.category_id','=',customer_categ.id),('invoice_date','=',date),('id','in',self.filter_data().ids)]
        

        moves=self.env['account.move'].search(domain)
        
        lines=self.env['account.move.line'].search([('display_type','=','product'),('move_id','in',moves.ids),('product_id.categ_id','=',pro_categ.id)])
        for line in lines:
            
            data['quantity']+=line.quantity
            data['total']+=line.price_subtotal
            data['grand_total']+=line.price_total
            data['discount']+=line.discount*line.price_unit*line.quantity
        
        return data


      



    def check(self):
        jj=self.get_dates()
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


    def generate_report(self):
        return self.env.ref('addis_systems_sales_reports.sales_sales_summary_report_report_customer_type').report_action(self)
