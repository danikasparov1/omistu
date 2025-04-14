import odoo.http as http

from odoo.exceptions import UserError,ValidationError
from odoo.http import request, content_disposition

import string
import time
import secrets
import json
import logging

import io
import csv

move_type = {
    'entry': 'Journal Entry',
    'out_invoice': 'Customer Invoice',
    'out_refund': 'Customer Credit Note',
    'in_invoice': 'Vendor Bill',
    'in_refund': 'Vendor Credit Note',
    'out_receipt': 'Sales Receipt',
    'in_receipt': 'Purchase Receipt',
}

def generate_token(length=32):
    characters = string.ascii_letters + string.digits
    token = ''.join(secrets.choice(characters) for _ in range(length))
    return token

class AccountMovePeachtree(http.Controller):
    @http.route(['/web/accountmovepeachtree/download'],type='http', auth="user")
    def download_account_move_peachtree(self, account_move_ids=None, **kwargs):
        if account_move_ids:
            account_move_ids = list(filter(None, (int(mid) for mid in account_move_ids.split(',') if mid.isdigit())))
            token = generate_token()
            file_name="unregistered"
            if request.env['account.move'].browse(account_move_ids[0]).move_type == "out_invoice":
                csv_data = self.get_customer_invoice_csv_data(request.env['account.move'].browse(account_move_ids))
                move_type_name = "Customer Invoice"
                file_name = f"{move_type_name}.csv"
            elif request.env['account.move'].browse(account_move_ids[0]).move_type == "in_invoice":
                csv_data = self.get_vendor_bill_csv_data(request.env['account.move'].browse(account_move_ids))
                move_type_name = "Vendor Bill"
                file_name = f"{move_type_name}.csv"
            elif request.env['account.move'].browse(account_move_ids[0]).move_type == "out_receipt":
                csv_data = self.get_receipt_csv_data(request.env['account.move'].browse(account_move_ids))
                move_type_name = "Sales Receipt"
                file_name = f"{move_type_name}.csv"
            else :
                raise ValidationError("Not Available")
            response = request.make_response(
                csv_data,
                headers=[
                    ('Content-Type', 'text/csv'),
                    ('Content-Disposition', content_disposition(file_name))
                ]
            )
            response.set_cookie('fileToken', token)
            return response

    def get_customer_invoice_csv_data(self, account_moves):
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
        headers = ["Trxn Name","Amount","ARAccountID","CustomerID","DateDue","GLAccountID","NumberOfRecords","SalesTaxAuthority","SerialNumber","TaxType","TrxDate","VoidedByTransaction","ItemID","Quantity","Description","UnitPrice"]
        writer.writerow(headers)
        for order in account_moves:
            total_order_lines=len(request.env["account.move.line"].search([('move_id','=',order.id),('display_type','=','product')]))
            for line in order.invoice_line_ids:
                if line.display_type == "product":
                    writer.writerow([
                        order.name,
                        f"{line.price_total:.2f}",
                        order.journal_id.default_account_id.code,
                        order.partner_id.partner_code,
                        order.invoice_date_due.strftime('%m/%d/%y') if order.invoice_date_due else '',
                        order.journal_id.default_account_id.code,
                        total_order_lines,
                        "",
                        "",
                        "",
                        order.invoice_date.strftime('%m/%d/%y') if order.invoice_date else '',
                        "",
                        line.product_id.default_code or '',
                        line.quantity,
                        
                        line.name,
                        f"{line.price_unit:.2f}",
                    ])

        output.seek(0)
        csv_data = output.getvalue()
        output.close()
        return csv_data
    


    def get_vendor_bill_csv_data(self, account_moves):
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
        headers = ["Amount","APAccountID","DateDue","GLAccountID","NumberOfRecords","RowCount","RowType","SerialNumber","TrxDate","ItemID","Quantity","Description","UnitPrice"]
        for order in account_moves:
            total_order_lines=len(request.env["account.move.line"].search([('move_id','=',order.id),('display_type','=','product')]))
            for line in order.invoice_line_ids:
                if line.display_type == "product":
                    writer.writerow([
                        f"{line.price_total:.2f}",
                        order.journal_id.default_account_id.code,
                        order.invoice_date_due.strftime('%m/%d/%y') if order.invoice_date_due else '',
                        order.journal_id.default_account_id.code,
                        total_order_lines,
                        total_order_lines,
                        "",
                        "",
                        order.invoice_date.strftime('%m/%d/%y') if order.invoice_date else '',
                        "",
                        line.product_id.default_code or '',
                        line.quantity,
                        
                        line.name,
                        f"{line.price_unit:.2f}",
                    ])

        output.seek(0)
        csv_data = output.getvalue()
        output.close()
        return csv_data
    


    def get_receipt_csv_data(self, account_moves):
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
        headers = ["Amount","APAccountID","DateDue","GLAccountID","NumberOfRecords","RowCount","RowType","SerialNumber","TrxDate","ItemID","Quantity","Description","UnitPrice"]
        for order in account_moves:
            total_order_lines=len(request.env["account.move.line"].search([('move_id','=',order.id),('display_type','=','product')]))
            for line in order.invoice_line_ids:
                if line.display_type == "product":
                    writer.writerow([
                        f"{line.price_total:.2f}",
                        order.journal_id.default_account_id.code,
                        order.invoice_date_due.strftime('%m/%d/%y') if order.invoice_date_due else '',
                        order.journal_id.default_account_id.code,
                        total_order_lines,
                        total_order_lines,
                        "",
                        "",
                        order.invoice_date.strftime('%m/%d/%y') if order.invoice_date else '',
                        "",
                        line.product_id.default_code or '',
                        line.quantity,
                        
                        line.name,
                        f"{line.price_unit:.2f}",
                    ])

        output.seek(0)
        csv_data = output.getvalue()
        output.close()
        return csv_data
    



    def get_receipts_csv_data(self, account_moves):
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
        headers = ["Amount","Cash Account ID","Discount Amount","GLAccountID","InvoicePaid","ItemID","NumberOfRecords","Quantity","Reference","RowCount","SalesTaxAuthority","SerialNumber","TaxType","TrxDate","UnitPrice"]
        for order in account_moves:
            total_order_lines=len(request.env["account.move.line"].search([('move_id','=',order.id),('display_type','=','product')]))
            for line in order.invoice_line_ids:
                if line.display_type == "product":
                    writer.writerow([
                        f"{line.price_total:.2f}",
                        order.journal_id.default_account_id.code,
                        line.discount*line.price_unit*line.quantity/100,
                        order.journal_id.default_account_id.code,
                        "",
                        line.product_id.default_code or '',
                        total_order_lines,
                        line.quantity,
                        order.payment_reference,
                        total_order_lines,
                        "",
                        "",
                        1,
                        order.invoice_date.strftime('%m/%d/%y') if order.invoice_date else '',
                        f"{line.price_unit:.2f}",
                    ])

        output.seek(0)
        csv_data = output.getvalue()
        output.close()
        return csv_data