from odoo import api, models,fields,_
from odoo.exceptions import ValidationError,UserError
from odoo import http
import pandas as pd
import io
import base64
import xlwt
from datetime import datetime
try:
    import xlrd
    try:
        from xlrd import xlsx
    except ImportError:
        xlsx = None
except ImportError:
    xlrd = xlsx = None
try:
    from . import odf_ods_reader
except ImportError:
    odf_ods_reader = None
    
class  InvoiceFile(models.TransientModel):
    _name="thirdpartyaddisysstems.invoice"
    name=fields.Char(string="Imported Invoice",default=lambda self: _('New'))
    invoice_file=fields.Binary(string='Invoice File',required=True)
    def download_newinvoice(self):
        try:
            new_workbook = xlwt.Workbook()
            new_sheet = new_workbook.add_sheet('Sheet1')
            binary_data = self.invoice_file
            decoded_data = base64.b64decode(binary_data)
            file_like_object = io.BytesIO(decoded_data)
            workbook = xlrd.open_workbook(file_contents=file_like_object.read())
            sheet = workbook.sheet_by_index(0)
            header_style = xlwt.XFStyle()
            font = xlwt.Font()
            font.bold = True
            header_style.font = font
            alignment = xlwt.Alignment()
            alignment.horz = xlwt.Alignment.HORZ_CENTER
            header_style.alignment = alignment
            pattern = xlwt.Pattern()
            pattern.pattern = xlwt.Pattern.SOLID_PATTERN
            pattern.pattern_fore_colour = xlwt.Style.colour_map['light_turquoise']
            header_style.pattern = pattern

            # Borders
            borders = xlwt.Borders()
            borders.bottom = xlwt.Borders.THIN
            header_style.borders = borders

            voucher=""
            new_sheet.write(0,0,"Number",header_style)
            new_sheet.write(0,1,"Date",header_style)
            new_sheet.write(0,2,"Customer Code",header_style)
            new_sheet.write(0,3,"Partner",header_style)
            new_sheet.write(0,4,"Invoice lines / Product",header_style)
            new_sheet.write(0,5,"Invoice lines / Unit Price",header_style)
            new_sheet.write(0,6,"Invoice lines / Quantity",header_style)
            new_sheet.write(0,7,"Invoice lines / Taxes",header_style)
            for row in range(1,sheet.nrows):
                voucher_code_xl=sheet.cell_value(row,0)
                date_xl=sheet.cell_value(row,1)
                date_tuple=xlrd.xldate_as_tuple(date_xl, workbook.datemode)
                date_value = datetime(*date_tuple)
                date_xl=date_value.strftime('%Y-%m-%d')
                partner_code_xl=sheet.cell_value(row,2)
                customer_name_xl=sheet.cell_value(row,3)
                product_xl=sheet.cell_value(row,6)
                price_unit_xl=sheet.cell_value(row,7)
                quantity_xl=sheet.cell_value(row,8)
                label_xl=sheet.cell_value(row,10)
                tax=""
                if sheet.cell_value(row,3) =="Null":
                    customer_name_xl=""
                if sheet.cell_value(row,2) =="Null":
                    partner_code_xl=""
                if voucher != sheet.cell_value(row,0):
                    new_sheet.write(row,0,voucher_code_xl)
                    new_sheet.write(row,1,date_xl)
                    new_sheet.write(row,2,partner_code_xl)
                    new_sheet.write(row,3,customer_name_xl)
                    new_sheet.write(row,4,product_xl)
                    new_sheet.write(row,5,price_unit_xl)
                    new_sheet.write(row,6,quantity_xl)
                else:
                    new_sheet.write(row,4,product_xl)
                    new_sheet.write(row,5,price_unit_xl)
                    new_sheet.write(row,6,quantity_xl)
                new_sheet.write(row,7,"")
                voucher=voucher_code_xl
            new_workbook.save(f'custom_modules/applications/addis_systems_data_pre_proccessor/static/data/invoice_xls/{self.name}.xls')
            return {
                'type': 'ir.actions.act_url',
                'url': f'/addis_systems_data_pre_proccessor/static/data/invoice_xls/{self.name}.xls',
                'target': 'self',
            }
        except:
            raise ValidationError("The given file format or its columns is not correct")
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _("New")) == _("New"):
                seq_date = fields.Datetime.context_timestamp(
                    self, fields.Datetime.to_datetime(vals['create_date'])
                ) if 'create_date' in vals else None
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'thirdpartyaddisysstems.invoice', sequence_date=seq_date) or _("New")
        return super().create(vals_list)
    

    


    