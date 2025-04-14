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
    _name="inventory.product.category.wizard"
    _description="Addissystems Inventory Product Category report"
    date_from = fields.Date(required=False)
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
        domain=[("product_id.type","!=","service"),("picking_type_id","!=",False)]
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
    

    def get_references(self,product_id):
        domain = self.get_constant_domain()
        domain+=[("product_id","=",product_id)]
        move_lines=self.env["stock.move.line"]._read_group(domain=domain, groupby=['reference'], aggregates=['quantity:sum'])
        return move_lines

    def get_operation_type(self,reference):
        op_type=self.env['stock.move.line'].search([("reference","=",reference)],limit=1)
        return op_type


    
    def get_products_under_category(self,categ_name):
        domain = self.get_constant_domain()
        domain+=[("product_category_name","=",categ_name)]
        move_lines=self.env["stock.move.line"]._read_group(domain,groupby=["product_id"],aggregates=['quantity:sum'])
        move_lines = sorted(move_lines, key=lambda x: x[0].display_name)
        return move_lines
        

    @api.onchange('warehouse_ids')
    def _onchange_warehouse_ids(self):
        if self.warehouse_ids:
            # Clear the stock_location_ids if warehouses are selected
            self.stock_location_ids = [(5, 0, 0)]

    def get_product_categories(self):
        domain = self.get_constant_domain()
        categs=self.env["stock.move.line"]._read_group(domain=domain,groupby=["product_category_name"],aggregates=['quantity:sum'])
        return categs
    

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
        return self.env.ref('addis_systems_stock_reports.action_print_report_inventory_product_category_html').report_action(self,data=data)

    def process_pdf(self):
        self.ensure_one()
        data={
        }

        data['form']=self.read(["date_from","date_to","warehouse_ids","stock_location_ids","product_ids","product_categ_ids","state"])[0]
        return self.env.ref('addis_systems_stock_reports.action_print_report_inventory_product_category_pdf').report_action(self,data=data)

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
                'report_name': f"Inventory Summary By Product Category"

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
        
        report_name = "Stock Summary by Product Category"
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
        sheet.merge_range('A1:D1', str(self.env.company.name), headings)
        # Write the report title
        sheet.merge_range('A2:D2', report_name, bold)
        
        # Write the date range description
        index = 2
        date_range = self.generate_date_label(wizard.date_from, wizard.date_to)
        sheet.write(index, 0, date_range, bold)
        
        # Header Row
        index += 1
        headers = ["Product Category", "Product", "Reference", "Quantity"]
        for col, header in enumerate(headers):
            sheet.write(index, col, header, header_format)
        
        # Data Rows
        index += 1
        for categ in wizard.get_product_categories():
            sheet.write(index, 0, categ[0], cell_format)
            sheet.write(index, 3, categ[1], number_format)
            index+=1
            for product in wizard.get_products_under_category(categ[0]):
                sheet.write(index, 1, product[0].name, cell_format)
                sheet.write(index, 3, product[1], number_format)
                index += 1
                for reference in wizard.get_references(product[0].id):
                        sheet.write(index, 2, reference[0], cell_format)
                        sheet.write(index, 3, reference[1], number_format)
                        index+=1
        workbook.close()
        output.seek(0)
        read_output = output.read()
        output.close()
        return read_output




    

    
