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
    _name="inventory.product.bincard.wizard"
    _description="Addissystems Inventory Product Date report"
    date_to = fields.Date(required=False)
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
        domain=[("product_id.type","!=","service")]
        if self.state :
            domain+=[("state","=",self.state)]
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

    

    @api.onchange('warehouse_ids')
    def _onchange_warehouse_ids(self):
        if self.warehouse_ids:
            # Clear the stock_location_ids if warehouses are selected
            self.stock_location_ids = [(5, 0, 0)]
    @api.onchange('product_categ_ids')
    def _onchange_warehouse_ids(self):
        if self.product_ids:
            # Clear the stock_location_ids if warehouses are selected
            self.product_ids = [(5, 0, 0)]
    
    def getlocation_id(self,location_id):
        location_data={
            "location_id":location_id,
            "opening_stock":0,
            "stock_in":0,
            "stock_out":0,
            "balance" :0,         
        }
        domain=self.get_constant_domain()
        domain+=["|",("location_id","=",location_id.id),("location_dest_id","=",location_id.id)]
        move_line_opening=self.env["stock.move.line"].search(domain)
        for line in move_line_opening:
            if not line.picking_type_id:
                location_data["opening_stock"]+=line.quantity
            elif line.location_dest_id.id==location_id.id:
                location_data["stock_out"]+=line.quantity
            elif line.location_id.id == location_id.id:
                location_data["stock_in"]+=line.quantity
            else:
                raise ValidationError("Something gets wrong")
            location_data["balance"]=location_data["opening_stock"]+location_data["stock_in"]-location_data["stock_out"]
        return location_data

    def get_data(self):
        data=[
        ]
        domain=self.get_constant_domain()
        locations=self.env["stock.move.line"].search(domain)
        locations=list(set(locations.location_id+locations.location_dest_id))
        for location in locations:
            location_data=self.getlocation_id(location)
            data.append(location_data)
        return data

    def preview_html(self):
        self.ensure_one()
        data={
        }

        data['form']=self.read(["date_to","warehouse_ids","stock_location_ids","product_ids","product_categ_ids","state"])[0]
        return self.env.ref('addis_systems_stock_reports.action_print_report_inventory_product_bincard_html').report_action(self,data=data)

    def process_pdf(self):
        self.ensure_one()
        data={
        }

        data['form']=self.read(["date_to","warehouse_ids","stock_location_ids","product_ids","product_categ_ids","state"])[0]
        return self.env.ref('addis_systems_stock_reports.action_print_report_inventory_product_bincard_pdf').report_action(self,data=data)

    def process_excel(self):
        self.ensure_one()
        data={
        }
        data['form']=self.read(["date_to","warehouse_ids","stock_location_ids","product_ids","product_categ_ids","state"])[0]
        data['active_id']=self.id
        data['active_model']=self._name
        return {
            'type': 'ir.actions.report',
            'report_type': 'excel',
            'data': {
                'model': self._name,
                'options': json.dumps(data, default=date_utils.json_default),
                'output_format': 'xlsx',
                'report_name': f"Bincard Summary"

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
        
        report_name = "Inventory Summary Bincard"
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
        
        # Write the report title
        headings = workbook.add_format({'font_size': '16px', 'align': 'center', 'bold': True, 'font_color': '#000000', 'bg_color': '#F1EEEE'})
        sheet.merge_range('A1:E1', str(self.env.company.name), headings)
        sheet.merge_range('A2:E2', report_name, bold)
        
        # Write the date range description
        index = 1
        date_range = self.generate_date_label(date_to=wizard.date_to)
        sheet.write(index, 0, date_range, bold)
        
        # Header Row
        index += 1
        headers = ["Stock", "Total Opening Stock", "Total Stock In ", "Total Stock Out ","Total Closing Stock"]
        for col, header in enumerate(headers):
            sheet.write(index, col, header, header_format)
        index += 1
        for location_data in wizard.get_data():
            sheet.write(index, 0, location_data['location_id'].name, cell_format)
            sheet.write(index, 1, location_data['opening_stock'], number_format)
            sheet.write(index, 2, location_data['stock_in'], number_format)
            sheet.write(index, 3, location_data['stock_out'], number_format)
            sheet.write(index, 4, location_data['balance'], number_format)
            index+=1

        workbook.close()
        output.seek(0)
        read_output = output.read()
        output.close()
        return read_output
