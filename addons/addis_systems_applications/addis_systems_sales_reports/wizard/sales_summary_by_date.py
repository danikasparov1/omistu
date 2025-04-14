from odoo import fields, models, api, _


class SalesSummaryReportByUser(models.TransientModel):
    _name = 'sales.summary.report.date'
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
    def get_move_lines(self,move_id=-1):
        data=self.env['account.move.line'].search([('move_id', '=' , move_id), ('display_type', '=', 'product')])
        return data

    def check_sales(self):
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
        moves=self.env['sale.order'].search(domain)
        data={

        }
        for move in moves:
            lines=self.env['sale.order.line'].search([('order_id', '=' , move.id)])
            discount=0
            for line in lines:
                disc=line.product_uom_qty*line.price_unit*line.discount/100
                discount += disc
            try:
                
                data[move.create_date.strftime("%Y-%m-%d")]["subtotal"]+=move.amount_untaxed
                data[move.create_date.strftime("%Y-%m-%d")]["discount"]+=discount
                data[move.create_date.strftime("%Y-%m-%d")]["total"]+=move.amount_total
                data[move.create_date.strftime("%Y-%m-%d")]["tax"]+=move.amount_total - move.amount_untaxed
            except:
                data[move.create_date.strftime("%Y-%m-%d")]={}
                data[move.create_date.strftime("%Y-%m-%d")]["subtotal"]=move.amount_untaxed
                data[move.create_date.strftime("%Y-%m-%d")]["discount"]=discount
                data[move.create_date.strftime("%Y-%m-%d")]["total"]=move.amount_total
                data[move.create_date.strftime("%Y-%m-%d")]["tax"]= move.amount_total - move.amount_untaxed
        return data


    def check(self):
        domain=[]
        if self.type != "invoice":
            return self.check_sales()
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
        moves=self.env['account.move'].search([('move_type', '=', 'out_invoice')]+domain)
        data={

        }
        for move in moves:
            lines=self.env['account.move.line'].search([('move_id', '=' , move.id), ('display_type', '=', 'product')])
            discount=0
            for line in lines:
                disc=line.quantity*line.price_unit*line.discount/100
                discount += disc
            try:
                
                data[move.date.strftime("%Y-%m-%d")]["subtotal"]+=move.amount_untaxed_signed
                data[move.date.strftime("%Y-%m-%d")]["discount"]+=discount
                data[move.date.strftime("%Y-%m-%d")]["total"]+=move.amount_total_signed
                data[move.date.strftime("%Y-%m-%d")]["tax"]+=move.amount_total_signed - move.amount_untaxed_signed
            except:
                data[move.date.strftime("%Y-%m-%d")]={}
                data[move.date.strftime("%Y-%m-%d")]["subtotal"]=move.amount_untaxed_signed
                data[move.date.strftime("%Y-%m-%d")]["discount"]=discount
                data[move.date.strftime("%Y-%m-%d")]["total"]=move.amount_total_signed
                data[move.date.strftime("%Y-%m-%d")]["tax"]= move.amount_total_signed - move.amount_untaxed_signed
        
        return data

    def generate_report_date(self):
        return self.env.ref('addis_systems_sales_reports.addis_sales_summary_report_report_date').report_action(self)
