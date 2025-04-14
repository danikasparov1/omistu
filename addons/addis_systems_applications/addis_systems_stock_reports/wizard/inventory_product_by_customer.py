
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import date_utils
from odoo.tools.misc import get_lang
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import io
import json
import xlsxwriter


class InventoryCategorizedCustomer(models.TransientModel):
    _name="inventory.category.customer.wizard"
    _description="Addissystems Stock expiry report"
    date_from = fields.Date(required=False)
    date_to = fields.Date(required=False)
    warehouse_ids=fields.Many2many(comodel_name="stock.warehouse", string="Warehouses")
    stock_location_ids=fields.Many2many(comodel_name="stock.location", string="Stock Locations")
    customer_ids=fields.Many2many(comodel_name="res.partner", string="Customers")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('assigned', 'Ready'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status',default="done"
        )

    @api.onchange('warehouse_ids')
    def _onchange_warehouse_ids(self):
        if self.warehouse_ids:
            # Clear the stock_location_ids if warehouses are selected
            self.stock_location_ids = [(5, 0, 0)]




    def get_constant_domain_closing(self):
        domain=[("picking_type_code","in",['incoming','outgoing'])]
        if self.state:
            domain+=[("state","=",self.state)]
            pass
        if self.date_to and self.state=="done":
            domain+=[("date_done","<",self.date_to)]
        if self.date_to and self.state=="done":
            domain+=[("scheduled_date","<",self.date_to)] 
        if self.stock_location_ids:
            domain+=["|",("location_dest_id","in",self.stock_location_ids.ids),("location_id","in",self.stock_location_ids.ids)]
        if self.warehouse_ids and not self.stock_location_ids:
            domain+=["|",("location_dest_id.warehouse_id","in",self.warehouse_ids.ids),("location_id.warehouse_id","in",self.warehouse_ids.ids)]
        if self.customer_ids:
            domain+=[("partner_id","in",self.customer_ids.ids)]
        return domain

    def get_constant_domain_opening(self):
        domain=[("picking_type_code","in",['incoming','outgoing'])]
        if self.state:
            domain+=[("state","=",self.state)]
        if self.date_from and self.state=="done":
            domain+=[("date_done","<",self.date_from)]

        if self.date_from and self.state=="done":
            domain+=[("scheduled_date","<",self.date_from)]

        if self.stock_location_ids:
            domain+=["|",("location_dest_id","in",self.stock_location_ids.ids),("location_id","in",self.stock_location_ids.ids)]
        if self.warehouse_ids and not self.stock_location_ids:
            domain+=["|",("location_dest_id.warehouse_id","in",self.warehouse_ids.ids),("location_id.warehouse_id","in",self.warehouse_ids.ids)]
        if self.customer_ids:
            domain+=[("partner_id","in",self.customer_ids.ids)]
        return domain
    


    def get_constant_domain(self):
        domain=[("picking_type_code","in",['incoming','outgoing'])]
        if self.state :
            domain+=[("state","=",self.state)]
            pass
        if self.date_from and self.state=="done":
            domain+=[("date_done",">=",self.date_from)]
        if self.date_to and self.state=="done":
            domain+=[("date_done","<=",self.date_to)]
        if self.date_from and self.state!="done":
            domain+=[("scheduled_date",">=",self.date_from)]
        if self.date_to and self.state!="done":
            domain+=[("scheduled_date","<=",self.date_to)]
        if self.stock_location_ids:
            domain+=["|",("location_dest_id","in",self.stock_location_ids.ids),("location_id","in",self.stock_location_ids.ids)]
        if self.warehouse_ids and not self.stock_location_ids:
            domain+=["|",("location_dest_id.warehouse_id","in",self.warehouse_ids.ids),("location_id.warehouse_id","in",self.warehouse_ids.ids)]
        if self.customer_ids:
            domain+=[("partner_id","in",self.customer_ids.ids)]
        return domain
        


        
    def get_opening_product_detail(self,product_id,partner_id):
        opening_stock =0
        domain=self.get_constant_domain_opening()
        domain+=[("partner_id","=",partner_id)]
        stock_picks=self.env["stock.picking"].search(domain)
        moves=self.env["stock.move"].search([("picking_id","in",stock_picks.ids),("product_id","=",product_id)])
        for move in moves:
            if move.picking_id.picking_type_code=="incoming":
                opening_stock+=move.quantity
            elif move.picking_id.picking_type_code=="outgoing":
                opening_stock-=move.quantity

        return opening_stock
    

    def get_closing_product_detail(self,product_id,partner_id):
        closing_stock =0
        domain=self.get_constant_domain_closing()
        domain+=[("partner_id","=",partner_id)]
        stock_picks=self.env["stock.picking"].search(domain)
        moves=self.env["stock.move"].search([("picking_id","in",stock_picks.ids),("product_id","=",product_id)])
        for move in moves:
            if move.picking_id.picking_type_code=="incoming":
                closing_stock+=move.quantity
            elif move.picking_id.picking_type_code=="outgoing":
                closing_stock-=move.quantity

        return closing_stock

   
    def get_product_detail(self,product_id,partner_id):
        data={

            "stock_in":0,
            "stock_out":0,
        }
        domain=self.get_constant_domain()
        domain+=[("partner_id","=",partner_id)]
        stock_picks=self.env["stock.picking"].search(domain)
        moves=self.env["stock.move"].search([("picking_id","in",stock_picks.ids),("product_id","=",product_id)])
        for move in moves:
            if move.picking_id.picking_type_code=="incoming":
                data["stock_in"]+=move.quantity
            elif move.picking_id.picking_type_code=="outgoing":
                data["stock_out"]+=move.quantity

        return data

    
    def get_products(self,partner_id):
        domain=self.get_constant_domain()
        domain+=[("partner_id","=",partner_id)]
        stock_picks=self.env["stock.picking"].search(domain)
        return stock_picks.move_ids.product_id
    
    def get_customers(self):
        domain=self.get_constant_domain()
        stock_picks=self.env["stock.picking"].search(domain)
        return stock_picks.partner_id
    
    def preview_html(self):
        self.ensure_one()
        data={
        }
        data['form']=self.read(["date_from","date_to","warehouse_ids","customer_ids"])[0]
        return self.env.ref('addis_systems_stock_reports.action_print_report_inventory_by_customer_html').report_action(self,data=data)
    
    def process_pdf(self):
        self.ensure_one()
        data={
        }
        data['form']=self.read(["date_from","date_to","warehouse_ids","customer_ids"])[0]
        return self.env.ref('addis_systems_stock_reports.action_print_report_inventory_by_customer_pdf').report_action(self,data=data)

    def process_excel(self):
        self.ensure_one()
        data={
        }
        data['form']=self.read(["date_from","date_to","warehouse_ids","customer_ids"])[0]
        data['active_id']=self.id
        data['active_model']='inventory.category.customer.wizard'
        return {
            'type': 'ir.actions.report',
            'report_type': 'excel',
            'data': {
                'model': 'inventory.category.customer.wizard',
                'options': json.dumps(data, default=date_utils.json_default),
                'output_format': 'xlsx',
                'report_name': f"Inventory Summary By Customer"
            }
        }
    
    def generate_date_label(self, date_from=None, date_to=None):
        if date_from and isinstance(date_from, str):
            date_from = datetime.strptime(date_from, "%Y-%m-%d").strftime("%B %d, %Y")
        elif date_from and isinstance(date_from, (date, datetime)):
            date_from = date_from.strftime("%B %d, %Y")
        
        if date_to and isinstance(date_to, str):
            date_to = datetime.strptime(date_to, "%Y-%m-%d").strftime("%B %d, %Y")
        elif date_to and isinstance(date_to, (date, datetime)):
            date_to = date_to.strftime("%B %d, %Y")
        
        if date_from and date_to:
            return f"From {date_from} to {date_to}"
        elif date_from:
            return f"From {date_from} onwards"
        elif date_to:
            return f"Up to {date_to}"
        else:
            return "No date range specified"



    def get_xlsx_report(self,data):
        if not (data.get('active_model') and data.get('active_id')):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        
        model = data.get('active_model')
        active_id = data.get('active_id')
        wizard = self.env[model].browse(active_id)
        
        report_name = "Stock Summary by Customer"
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet(report_name[:31])  # Excel sheet name limited to 31 characters
        
        # Formatting styles
        bold = workbook.add_format({'bold': True, 'font_size': 16})
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#D3D3D3',
            'border': 1
        })
        cell_format = workbook.add_format({
            'font_size': 10,
            'border': 1,
            'align': 'left'
        })
        number_format = workbook.add_format({
            'font_size': 10,
            'border': 1,
            'align': 'right',
            'num_format': '0.00'  # Ensures numbers are formatted with two decimal places
        })
        date_format = workbook.add_format({
            'font_size': 10,
            'border': 1,
            'align': 'left',
            'num_format': 'yyyy-mm-dd'
        })
        
        # Set column widths
        sheet.set_column('A:A', 40)  # Customer names
        sheet.set_column('B:B', 40)  # Product names
        sheet.set_column('C:F', 20)  # Stock columns
        
        # Set row heights
        sheet.set_row(0, 30)  # Title row
        sheet.set_row(1, 20)  # Date range row
        headings = workbook.add_format({'font_size': '16px', 'align': 'center', 'bold': True, 'font_color': '#000000', 'bg_color': '#F1EEEE'})
        sheet.merge_range('A1:F1', str(self.env.company.name), headings)

        # Write the report title
        sheet.merge_range('A2:F2', report_name, bold)
        
        # Write the date range description
        index = 2
        date_range = self.generate_date_label(wizard.date_from, wizard.date_to)
        sheet.write(index, 0, date_range, bold)
        
        # Header Row
        index += 1
        headers = ["Customer", "Product", "Total Opening Stock", "Total Stock In", "Total Stock Out", "Total Closing Stock"]
        for col, header in enumerate(headers):
            sheet.write(index, col, header, header_format)
        
        # Data Rows
        index += 1
        for partner in wizard.get_customers():
            sheet.write(index, 0, partner.name, cell_format)
            for product in wizard.get_products(partner.id):
                product_data = wizard.get_product_detail(product.id, partner.id)
                opening_stock = wizard.get_opening_product_detail(product.id, partner.id)
                closing_stock = wizard.get_closing_product_detail(product.id, partner.id)
                
                sheet.write(index, 1, product.name, cell_format)
                sheet.write(index, 2, opening_stock, number_format)
                sheet.write(index, 3, product_data.get('stock_in'), number_format)
                sheet.write(index, 4, product_data.get('stock_out'), number_format)
                sheet.write(index, 5, closing_stock, number_format)
                index += 1
        workbook.close()
        output.seek(0)
        read_output = output.read()
        output.close()
        return read_output


    