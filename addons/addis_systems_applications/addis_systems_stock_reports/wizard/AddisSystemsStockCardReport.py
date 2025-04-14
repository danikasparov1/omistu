from odoo import fields, models, api
from odoo.tools import date_utils
import io
import json
import xlsxwriter


class AddisSystemsStockCardReport(models.TransientModel):
    _name = 'report.stock.move.stock.card'
    _description = 'Addis Systems Stock Card'

    company_id = fields.Many2one(
        'res.company', string='Company', required=True, default=lambda self: self.env.company)
    stock_location = fields.Many2one(
        'stock.location', "Location", required=True, company_dependent=True, check_company=True)

    product_category = fields.Many2one(
        'product.category', string='Product Category')
    category_products = fields.Many2many(
        'product.product', compute='_category_products_list')

    product_id = fields.Many2one(
        'product.product', string='Product', domain="[('active', '=', True)]")
    product_template_id = fields.Many2one(related='product_id.product_tmpl_id')

    date_from = fields.Date(string="From Date")
    date_to = fields.Date(string="To Date")

    product_moves = fields.One2many('stock.move.line', compute='_stock_moves')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.product_category = None

    @api.onchange('product_category')
    def _onchange_product_category(self):
        if self.product_category:
            self.product_id = None

    @api.onchange('product_id', 'stock_location', 'product_category')
    def _stock_moves(self):
        domain = [('state', '=', 'done')]

        if self.product_category or self.product_id:
            if self.product_category:
                domain += [('product_id.product_tmpl_id.categ_id',
                            '=', self.product_category.id)]
            elif self.product_id:
                domain += [('product_id', '=', self.product_id.id)]
        if self.stock_location:
            domain += ['|', ('location_id', '=', self.stock_location.id),
                       ('location_dest_id', '=', self.stock_location.id)]

        self.product_moves = self.env['stock.move.line'].search(
            domain, order='date')

    @api.onchange('product_category')
    def _category_products_list(self):
        domain = [('active', 'in', [True, False])]
        if self.product_category:
            domain += [('product_tmpl_id.categ_id',
                        '=', self.product_category.id)]
        self.category_products = self.env['product.product'].search(domain)

    def product_done_moves_count(self, product_id, move_ids):
        return self.env['stock.move.line'].search_count([('id', 'in', move_ids.ids), ('product_id', '=', product_id.id)])

    def category_product_moves(self, product_id, move_ids):
        return self.env['stock.move.line'].search([('id', 'in', move_ids.ids), ('product_id', '=', product_id.id)], order='date')

    # NOTE ------------------------------------   Processing Data Printing and Preview    ------------------------------------

    def preview_html(self):
        if self.product_id and self.product_category:
            self.product_category = None
        return self.env.ref('addis_systems_stock_reports.report_addis_systems_stock_card_report_html').report_action(self)

    def process_pdf(self):
        if self.product_id and self.product_category:
            self.product_category = None
        return self.env.ref('addis_systems_stock_reports.report_addis_systems_stock_card_report_pdf').report_action(self)

    # NOTE EXCEL

    def process_excel(self):
        stock_card_data = {
            'company_id': self.company_id.id,
            'stock_location': self.stock_location.id,
            'product_category': self.product_category.id,
            'category_products': self.category_products.ids,
            'product_id': self.product_id.id,
            'product_template_id': self.product_template_id.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'product_moves': self.product_moves.ids,
            'user_id': self.env.user.id
        }
        return {
            'type': 'ir.actions.report',
            'report_type': 'excel',
            'data': {
                'model': 'report.stock.move.stock.card',
                'options': json.dumps(stock_card_data, default=date_utils.json_default),
                'output_format': 'xlsx',
                'report_name': f"Stock Card - {self.stock_location.complete_name} {self.product_category.name or self.product_id.name}"
            }
        }

    def get_xlsx_report(self, data):
        stock_location = self.env['stock.location'].search([('id', '=', data['stock_location'])], limit=1) or None
        product_category = self.env['product.category'].search([('id', '=', data['product_category'])], limit=1) if 'product_category' in data and data['product_category'] else None
        product_id = self.env['product.product'].search([('id', '=', data['product_id'])], limit=1) if 'product_id' in data and data['product_id'] else None
        product_template_id = self.env['product.product'].search([('id', '=', data['product_id'])], limit=1).product_tmpl_id if 'product_id' in data and data['product_id'] else None
        date_from = data['date_from'] or None
        date_to = data['date_to'] or None

        category_products = self.env['product.product'].search([('id', 'in', data['category_products'])]) if 'category_products' in data and data['category_products'] else None
        product_moves = self.env['stock.move.line'].search([('id', 'in', data['product_moves'])]) if 'product_moves' in data and data['product_moves'] else None

        title = f"Stock Card - {stock_location.complete_name} From {date_from} - {date_to}" if date_from and date_to else f"Stock Card - {stock_location.complete_name} All"

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet("Inventory Report's")

        headings = workbook.add_format({'font_size': '16px', 'align': 'center', 'bold': True, 'font_color': '#000000', 'bg_color': '#F1EEEE'})
        head = workbook.add_format({'font_size': '12px', 'align': 'left', 'bold': True})
        head_center = workbook.add_format({'font_size': '12px', 'align': 'center', 'bold': True})
        cell_format_center = workbook.add_format({'font_size': '12px', 'align': 'center'})
        cell_format_right = workbook.add_format({'font_size': '12px', 'align': 'right'})
        cell_format_left = workbook.add_format({'font_size': '12px', 'align': 'left'})
        cell_format_left_bold = workbook.add_format({'font_size': '12px', 'align': 'left', 'bold': True, 'bg_color': '#F1EEEE'})

        sheet.merge_range('A1:F1', str(self.env.company.name), headings)
        sheet.merge_range('A2:F2', title, head_center)
        sheet.set_row(0, 20)
        sheet.set_row(1, 15)
        sheet.set_column(0, 0, 20)
        sheet.set_column(1, 1, 30)
        sheet.set_column(2, 2, 10)
        sheet.set_column(3, 3, 10)
        sheet.set_column(4, 4, 10)
        sheet.set_column(5, 5, 30)

        sheet.merge_range('A3:A4', "Date", head)
        sheet.merge_range('B3:B4', "Reference", head)
        sheet.merge_range('C3:E3', "Quantity", head_center)
        sheet.write(3, 2, "Received", head_center)
        sheet.write(3, 3, "Issued", head_center)
        sheet.write(3, 4, "Balance", head_center)
        sheet.merge_range('F3:F4', "Partner", head_center)

        row_index = 4
        quantity_on_hand = 0
        if product_category and category_products:
            for product in category_products:
                quantity_on_hand = 0
                product_move_lines = self.product_done_moves_count(product, product_moves)
                if product_move_lines != 0:
                    row_index = row_index + 1
                    sheet.merge_range(f'A{row_index}:F{row_index}', f"[{product.default_code}] {product.name}" if product.default_code else str(product.name), cell_format_left_bold)
                    for line in self.category_product_moves(product, product_moves):
                        sheet.write(row_index, 0, line.date.strftime('%d-%m-%Y %H:%M:%S'), cell_format_left)
                        received = line.quantity if line.location_dest_id.id == stock_location.id else 0
                        issued = line.quantity if line.location_id.id == stock_location.id else 0
                        if line.location_dest_id.id == stock_location.id:
                            quantity_on_hand = quantity_on_hand + line.quantity
                        elif line.location_id.id == stock_location.id:
                            quantity_on_hand = quantity_on_hand - line.quantity
                        sheet.write(row_index, 0, line.date.strftime('%d-%m-%Y %H:%M:%S'), cell_format_left)
                        sheet.write(row_index, 1, line.reference, cell_format_left)
                        sheet.write(row_index, 2, received if received != 0 else '', cell_format_right)
                        sheet.write(row_index, 3, issued if issued != 0 else '', cell_format_right)
                        sheet.write(row_index, 4, quantity_on_hand, cell_format_right)
                        sheet.write(row_index, 5, line.picking_id.partner_id.name if line.picking_id.partner_id.name not in [0, False, ''] else '', cell_format_left)
                        row_index = row_index + 1
        elif not product_category and product_id:
            for line in product_moves:
                received = line.quantity if line.location_dest_id.id == stock_location.id else 0
                issued = line.quantity if line.location_id.id == stock_location.id else 0
                if line.location_dest_id.id == stock_location.id:
                    quantity_on_hand = quantity_on_hand + line.quantity
                elif line.location_id.id == stock_location.id:
                    quantity_on_hand = quantity_on_hand - line.quantity
                sheet.write(row_index, 0, line.date.strftime('%d-%m-%Y %H:%M:%S'), cell_format_left)
                sheet.write(row_index, 1, line.reference, cell_format_left)
                sheet.write(row_index, 2, received if received != 0 else '', cell_format_right)
                sheet.write(row_index, 3, issued if issued != 0 else '', cell_format_right)
                sheet.write(row_index, 4, quantity_on_hand, cell_format_right)
                sheet.write(row_index, 5, line.picking_id.partner_id.name if line.picking_id.partner_id.name not in [0, False, ''] else '', cell_format_left)
                row_index = row_index + 1

        workbook.close()
        output.seek(0)
        read_output = output.read()
        output.close()
        return read_output
