from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import date_utils
from odoo.tools.misc import get_lang
from datetime import datetime, date,timedelta
from dateutil.relativedelta import relativedelta
import io
import json
import xlsxwriter

class InventoryCategorizedDate(models.TransientModel):
    _name="inventory.product.trxname.wizard"
    _description="Addissystems Inventory Product Transaction name report"
    date_from = fields.Date(required=False)
    date_to = fields.Date(required=False)
    stock_picking_type=fields.Many2many(comodel_name="stock.picking.type", string="Operation Type")
    warehouse_ids=fields.Many2many(comodel_name="stock.warehouse", string="Warehouses")
    stock_location_ids=fields.Many2many(comodel_name="stock.location", string="Stock Locations")
    product_ids=fields.Many2many(comodel_name="product.product", string="Products")
    product_categ_ids=fields.Many2many(comodel_name="product.category", string="Product Categories")
    state = fields.Selection([
        ('draft', 'New'),
        ('waiting', 'Waiting Another Move'),
        ('confirmed', 'Waiting Availability'),
        ('partially_available', 'Partially Available'),
        ('assigned', 'Available'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')]
        , string='Status',default="done"
        )
    
    def get_constant_domain(self):
        domain=[("product_id.type","!=","service"),("picking_type_id","!=",False)]
        if self.stock_picking_type:
            domain+=[("picking_type_id","in",self.stock_picking_type.ids)]
        if self.state :
            domain+=[("state","=",self.state)]
        if self.date_from:
            domain+=[("date",">=",self.date_from)]
        if self.date_to :
            domain+=[("date","<=",self.date_to)]
        if self.stock_location_ids:
            domain+=["|",("location_dest_id","in",self.stock_location_ids.ids),("location_id","in",self.stock_location_ids.ids)]
        if self.warehouse_ids and not self.stock_location_ids:
            domain+=["|",("location_dest_id.warehouse_id","in",self.warehouse_ids.ids),("location_id.warehouse_id","in",self.warehouse_ids.ids)]
        if self.product_ids:
            domain+=[("product_id","in",self.product_ids.ids)]
        if self.product_categ_ids and not self.product_ids:
            domain+=[("product_id.categ_id","in",self.product_categ_ids.ids)]
        return domain
    

    def get_operation_type(self,reference):
        op_type=self.env['stock.move.line'].search([("reference","=",reference)],limit=1)
        return op_type
    
    # def get_references(self,product_id,categ_name):
    #     domain = self.get_constant_domain()
    #     current_date=categ_name
    #     next_date=categ_name+ + timedelta(days=1)
    #     domain+=[("date",">=",current_date),("date","<",next_date)]
    #     domain+=[("product_id","=",product_id)]
    #     move_lines=self.env["stock.move.line"]._read_group(domain=domain, groupby=['reference'], aggregates=['quantity:sum'])
    #     return move_lines



    
    def get_products_under_reference_date(self,reference,date_under):
        current_date=date_under
        next_date=date_under+ + timedelta(days=1)
        domain = self.get_constant_domain()
        domain+=[("date",">=",current_date),("date","<",next_date)]
        domain+=[("reference","=",reference)]
        move_lines=self.env["stock.move.line"]._read_group(domain,groupby=["product_id"],aggregates=['quantity:sum'])
        move_lines = sorted(move_lines, key=lambda x: x[0].display_name)
        return move_lines
        

    @api.onchange('warehouse_ids')
    def _onchange_warehouse_ids(self):
        if self.warehouse_ids:
            # Clear the stock_location_ids if warehouses are selected
            self.stock_location_ids = [(5, 0, 0)]

    def get_references(self,op_type):
        domain = self.get_constant_domain()
        domain+=[("picking_type_id","=",op_type)]
        references=self.env["stock.move.line"]._read_group(domain=domain,groupby=["reference"],aggregates=['quantity:sum'])
        return references
    
    def get_location_quantity(self,reference,date_under,product_id):
        current_date=date_under
        next_date=date_under+ + timedelta(days=1)
        domain = self.get_constant_domain()
        domain+=[("date",">=",current_date),("date","<",next_date)]
        domain+=[("product_id","=",product_id)]
        move_lines=self.env["stock.move.line"]._read_group(domain,groupby=["product_id"],aggregates=['quantity:sum'])
        move_lines = sorted(move_lines, key=lambda x: x[0].display_name)


    def get_dates_under_reference(self,reference):
        domain = self.get_constant_domain()
        domain+=[("reference","=",reference)]
        dates=self.env["stock.move.line"]._read_group(domain=domain,groupby=["date:day"],aggregates=['quantity:sum'])
        dates=[(i.date(),j) for i, j in dates]
        return dates
    
    def get_quantity_op_type(self,op_type):
        domain = self.get_constant_domain()
        domain+=[("picking_type_id","=",op_type)]
        move_lines = self.env['stock.move.line'].search(domain)
        total_quantity = sum(move_line.quantity for move_line in move_lines)
        return total_quantity
        
    def get_operation_types(self):
        domain = self.get_constant_domain()
        op_types_data=[]
        op_types = self.env["stock.move.line"].search(domain=domain).picking_type_id
        data=[(op_type,self.get_quantity_op_type(op_type.id)) for op_type in op_types]
        return data


    @api.onchange('product_categ_ids')
    def _onchange_warehouse_ids(self):
        if self.product_ids:
            # Clear the stock_location_ids if warehouses are selected
            self.product_ids = [(5, 0, 0)]


    def preview_html(self):
        self.ensure_one()
        data={
        }

        data['form']=self.read(["date_from","date_to","warehouse_ids","stock_location_ids","product_ids","product_categ_ids","state"])[0]
        return self.env.ref('addis_systems_stock_reports.action_print_report_inventory_product_trxname_html').report_action(self,data=data)
    def process_pdf(self):
        self.ensure_one()
        data={
        }

        data['form']=self.read(["date_from","date_to","warehouse_ids","stock_location_ids","product_ids","product_categ_ids","state"])[0]
        return self.env.ref('addis_systems_stock_reports.action_print_report_inventory_product_trxname_pdf').report_action(self,data=data)


    def process_excel(self):
        self.ensure_one()
        data={
        }
        data['form']=self.read(["date_from","date_to","warehouse_ids","stock_location_ids","product_ids","product_categ_ids","state"])[0]
        data['active_id']=self.id
        data['active_model']=self._name
        return {
            'type': 'ir.actions.report',
            'report_type': 'excel',
            'data': {
                'model': self._name,
                'options': json.dumps(data, default=date_utils.json_default),
                'output_format': 'xlsx',
                'report_name': f"Stock Summary By Transaction name"

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



    def get_xlsx_report(self, data):
        if not (data.get('active_model') and data.get('active_id')):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        
        model = data.get('active_model')
        active_id = data.get('active_id')
        wizard = self.env[model].browse(active_id)
        
        report_name = "Stock Summary By Transaction name"
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
        sheet.set_column('C:C', 20)  # Stock columns
        sheet.set_column('D:D', 40)
        # Set row heights
        sheet.set_row(0, 30)  # Title row
        sheet.set_row(1, 20)  # Date range row
        
        # Write the report title
        headings = workbook.add_format({'font_size': '16px', 'align': 'center', 'bold': True, 'font_color': '#000000', 'bg_color': '#F1EEEE'})
        sheet.merge_range('A1:F1', str(self.env.company.name), headings)
        sheet.merge_range('A2:F2', report_name, bold)
        
        # Write the date range description
        index = 1
        date_range = self.generate_date_label(wizard.date_from, wizard.date_to)
        sheet.write(index, 0, date_range, bold)
        
        # Header Row
        index += 1
        headers = ["Transaction Name", "Transaction ID", "Date", "Product","In","Out"]
        for col, header in enumerate(headers):
            sheet.write(index, col, header, header_format)
        
  
        # Data Rows
        index += 1
        for op_type in wizard.get_operation_types():
            print("newww")
            print(op_type)
            sheet.write(index, 0, op_type[0].name, cell_format)
            sheet.write(index, 5, op_type[1], number_format)
            index+=1
            for ref in wizard.get_references(op_type[0].id):
                sheet.write(index, 1, ref[0], cell_format)
                if wizard.get_operation_type(ref[0]).picking_type_id.code in ['incoming','mrp_operation']:
                    sheet.write(index, 4, ref[1], number_format)
                else:
                    sheet.write(index, 5, ref[1], number_format)

                index+=1
                for date_cr in wizard.get_dates_under_reference(ref[0]):
                    sheet.write(index, 2, date_cr[0].strftime("%B %d, %Y"), cell_format)
                    if wizard.get_operation_type(ref[0]).picking_type_id.code in ['incoming','mrp_operation']:
                        sheet.write(index, 4, ref[1], number_format)
                    else:
                        sheet.write(index, 5, ref[1], number_format)
                    index += 1
                    for product in wizard.get_products_under_reference_date(ref[0],date_cr[0]):
                            sheet.write(index, 3, product[0].display_name, number_format)
                            if wizard.get_operation_type(ref[0]).picking_type_id.code in ['incoming','mrp_operation']:
                                sheet.write(index, 4, product[1], number_format)
                            else:
                                sheet.write(index, 5, product[1], number_format)
                            index+=1

        workbook.close()
        output.seek(0)
        read_output = output.read()
        output.close()
        return read_output




    
