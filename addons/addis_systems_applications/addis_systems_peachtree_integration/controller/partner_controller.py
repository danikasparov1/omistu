import odoo.http as http

from odoo.exceptions import UserError
from odoo.http import request, content_disposition

import string
import time
import secrets
import json
import logging

import json
import csv
import io

def generate_token(length=32):
    characters = string.ascii_letters + string.digits
    token = ''.join(secrets.choice(characters) for _ in range(length))
    return token

class ProductPeachtree(http.Controller):
    @http.route(['/web/partnerpeachtree/download'],type='http', auth="user")
    def download_product_peachtree(self, partner_ids=None, **kwargs):
        if partner_ids:
            partner_ids = list(filter(None, (int(mid) for mid in partner_ids.split(',') if mid.isdigit())))
            token = generate_token()
            aa = self.get_csv_data(request.env['res.partner'].browse(partner_ids))
            file_name = "partners"
            response = request.make_response(
                aa,
                headers=[
                    ('Content-Type', 'text/csv'),
                    ('Content-Disposition', content_disposition(f"{file_name}.csv"))
                ]
            )
            response.set_cookie('fileToken', token)
            return response

    def get_csv_data(self, partners):
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Determine the header based on partner type
        if partners and partners[0].customer_rank >= 0:
            headers = ["Customer ID", "Customer Name","G/L Sales Account"]
        elif partners and partners[0].supplier_rank >= 0:
            headers = ["Vendor ID", "Vendor Name","Expense Account"]
        else:
            headers = ["Partner ID", "Partner Name","Account Receivable"]

        # Write the header row
        writer.writerow(headers)
        
        # Write data rows
        for partner in partners:
            if not partner.partner_code:
                pass
            if partner.customer_rank >= 0:
                writer.writerow([partner.partner_code, partner.name,partner.property_account_receivable_id.code.replace(".","-")])  # For customers
            elif partner.supplier_rank >= 0:
                writer.writerow([partner.id, partner.name,partner.name,partner.property_account_payable_id.replace(".","-")])  # For vendors
            else:
                writer.writerow([partner.id, partner.name])  # Generic case
        
        output.seek(0)
        return output.getvalue()

