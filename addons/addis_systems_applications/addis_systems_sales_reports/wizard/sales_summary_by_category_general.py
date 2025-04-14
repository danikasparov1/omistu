from odoo import fields, models, api, _


class SalesSummaryReportByCategory(models.TransientModel):
    _name = 'sales.summary.report.category.general'
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    user_id = fields.Many2one('res.users',string="Cashier")
    customer_id = fields.Many2one('res.partner')
    product_categ_ids=fields.Many2many(comodel_name="product.category", string="Product Categories")
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
    def get_constant_domain_sales(self):
        domain=[("order_id.state","=",self.type)]
        if self.date_from:
            domain += [('order_id.date_order', '>=', self.date_from)]
        if self.date_to:
            domain += [('order_id.date_order', '<=', self.date_to)]
        if self.customer_id:
            domain += [('order_id.partner_id', '=', self.customer_id.id)]
        if self.user_id:
            domain+=[('order_id.create_uid', '=', self.user_id.id)]
        return domain
    
    def  get_constant_domain_invoice(self):
        domain=[('move_id.move_type', '=', 'out_invoice'),("display_type","=","product")]
        if self.date_from:
            domain += [('move_id.date', '>=', self.date_from)]
        if self.date_to:
            domain += [('move_id.date', '<=', self.date_to)]
        if self.journal:
            move_ids=self.env['account.payment'].search([('journal_id','=',self.journal.id)]).reconciled_invoice_ids.ids
            domain+=[('move_id.id','in',move_ids)]
        if self.status:
            domain += [('move_id.state', '=', self.status)]
        if self.payment_status:
            domain+=[('move_id.payment_state','=',self.payment_status)]    
        if self.customer_id:
            domain += [('move_id.partner_id', '=', self.customer_id.id)]
        if self.user_id:
            domain+=[('move_id.create_uid', '=', self.user_id.id)]
        return domain

    def get_product_categories(self):
        if self.type =='invoice':
            domain = self.get_constant_domain_invoice()
            categs=self.env["account.move.line"].search(domain).product_id.categ_id
        else:
            domain = self.get_constant_domain_sales()
            sale_order_line=self.env["sale.order.line"].search(domain)
            categs=sale_order_line.product_template_id.categ_id   
        return categs
    
    def get_product_under_category(self,categ_id):
        if self.type == "invoice":
            domain = self.get_constant_domain_invoice()
            domain+=[('product_id.categ_id','=',categ_id)]
            move_lines=self.env["account.move.line"].search(domain)
            return move_lines.product_id
        domain = self.get_constant_domain_sales()
        domain+=[('product_template_id.categ_id','=',categ_id)]
        sale_order_line=self.env["sale.order.line"].search(domain)
        return sale_order_line.product_template_id
            
    def get_product_data_invoiced(self,pro_id):
        data={
            "quantity":0,
            "unit_price":0,
            "tax":0,
            "subtotalamount":0,
            "discount":0,
            "total_amount":0
        }
        domain = self.get_constant_domain_invoice()
        domain+=[("product_id","=",pro_id)]
        move_lines=self.env['account.move.line'].search(domain)
        for line in move_lines:
            data["quantity"]+=line.quantity
            data["unit_price"]+=line.price_unit
            data["subtotalamount"]+=line.price_subtotal
            data["total_amount"]+=line.price_total
            data["discount"]+=line.quantity*line.price_unit*line.discount/100
        data["tax"] = data["total_amount"]-data["subtotalamount"]
        return data
    
    def get_product_data(self,pro_id):
        if self.type == "invoice":
            return self.get_product_data_invoiced(pro_id=pro_id)
        data={
            "quantity":0,
            "unit_price":0,
            "tax":0,
            "subtotalamount":0,
            "discount":0,
            "total_amount":0
        }
        domain = self.get_constant_domain_sales()
        domain+=[("product_template_id","=",pro_id)]
        sale_order_line=self.env["sale.order.line"].search(domain)
        for line in sale_order_line:
            data["quantity"]+=line.product_uom_qty
            data["unit_price"]+=line.price_unit
            data["subtotalamount"]+=line.price_subtotal
            data["total_amount"]+=line.price_total
            data["discount"]+=line.product_uom_qty*line.price_unit*line.discount/100
        data["tax"] = data["total_amount"]-data["subtotalamount"]
        return data
 
    def generate_report_category(self):
        return self.env.ref('addis_systems_sales_reports.sales_summary_report_category_general').report_action(self)
