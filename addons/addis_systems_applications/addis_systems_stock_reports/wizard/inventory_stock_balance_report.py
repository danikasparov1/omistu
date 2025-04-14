from odoo import fields, models, api
from odoo.tools import date_utils
from odoo.exceptions import UserError, ValidationError

import io
import json
import xlsxwriter

class AddisSystemsStockBalanceReport(models.TransientModel):
    _name = 'report.stock.move.stock.balance'
    _description = 'Addis Systems Stock balance Report'

    company_id = fields.Many2one(
        'res.company', string='Company', required=True, default=lambda self: self.env.company)
    date_from = fields.Date(string="From Date")
    date_to = fields.Date(string="To Date")
    product_ids=fields.Many2many(comodel_name="product.product", string="Products")
    product_categ_ids=fields.Many2many(comodel_name="product.category", string="Product Categories")



    def get_locations(self):
        return self.env['stock.quant'].search([]).location_id
    def get_quantity(self,product,location):
        domain=[('product_id','=',product.id),('location_id','=',location.id)]
        quants=self.env['stock.quant'].search(domain)
        total_quant=sum(quant.inventory_quantity_auto_apply for quant in quants)
        return total_quant
    def get_products(self):
        domain=[]
        if self.product_categ_ids and not self.product_ids:
            domain+=[("categ_id",'in',self.product_categ_ids.ids)]
        elif self.product_ids:
            domain+=[("id",'in',self.product_ids.ids)]
        products=self.env['product.product'].search(domain)
        return products

    def preview_html(self):
        return self.env.ref('addis_systems_stock_reports.report_addis_systems_stock_balance_report_html').report_action(self)

    def process_pdf(self):
        if self.product_id and self.product_category:
            self.product_category = None
        return self.env.ref('addis_systems_stock_reports.report_addis_systems_stock_balance_report_pdf').report_action(self)

    # NOTE EXCEL

    def process_excel(self):
        data = {
        "active_id" : self.id,
        "active_model" : self._name
        }

        return {
            'type': 'ir.actions.report',
            'report_type': 'excel',
            'data': {
                'model': 'report.stock.move.stock.balance',
                'options': json.dumps(data, default=date_utils.json_default),
                'output_format': 'xlsx',
                'report_name': f"Stock Balance"
            }
        }
    


    def get_xlsx_report(self, data):
        if not (data.get('active_model') and data.get('active_id')):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        
        model = data.get('active_model')
        active_id = data.get('active_id')
        wizard = self.env[model].browse(active_id)
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        
        report_name = "Stock Balance"
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
        headers = wizard.get_locations()
        # Set column widths
        sheet.set_column(f'A:{chr(len(headers)+65)}', 40)  # Customer names
        
        # Set row heights
        sheet.set_row(0, 30)  # Title row
        headings = workbook.add_format({'font_size': '16px', 'align': 'center', 'bold': True, 'font_color': '#000000', 'bg_color': '#F1EEEE'})
        sheet.merge_range(f'A1:{chr(len(headers)+65)}1', str(self.env.company.name), headings)
        # Write the report title
        sheet.merge_range(f'A2:{chr(len(headers)+65)}2', report_name, headings)
        
        # Write the date range description
        index = 2    
        sheet.write(index, 0, 'Product', header_format)
        for col, header in enumerate(headers):
            sheet.write(index, col+1, header.display_name, header_format)
        
        # Data Rows
        index += 1
        for product in wizard.get_products():
            col=0
            sheet.write(index, 0, product.display_name, cell_format)
            col+=1
            for location in headers:
                sheet.write(index, col, wizard.get_quantity(product,location), cell_format)
                col+=1
            index += 1
                
        workbook.close()
        output.seek(0)
        read_output = output.read()
        output.close()
        return read_output

