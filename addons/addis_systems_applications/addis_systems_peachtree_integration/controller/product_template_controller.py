import odoo.http as http

from odoo.exceptions import UserError
from odoo.http import request, content_disposition

import string
import time
import secrets
import json
import logging

import io
import json
import csv

product_categ_dictionary={
    "consu":4,
    "service":4,
    "product":1,
}
def generate_token(length=32):
    characters = string.ascii_letters + string.digits
    token = ''.join(secrets.choice(characters) for _ in range(length))
    return token

class ProductPeachtree(http.Controller):
    @http.route(['/web/productpeachtree/download'],type='http', auth="user")
    def download_product_peachtree(self, product_template_ids=None, **kwargs):
        if product_template_ids:
            product_template_ids = list(filter(None, (int(mid) for mid in product_template_ids.split(',') if mid.isdigit())))
            token = generate_token()
            csv_data = self.get_csv_data(request.env['product.template'].browse(product_template_ids))
            file_name = "products"
            
            response = request.make_response(
                csv_data,
                headers=[
                    ('Content-Type', 'text/csv'),
                    ('Content-Disposition', content_disposition(f"{file_name}.csv"))
                ]
            )
            response.set_cookie('fileToken', token)
            return response

    def get_csv_data(self, products):
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
        
        # Write headers
        headers = ["ItemID","Item Description","Item Class" , "Sales Price 1", "Last Unit Cost","G/L Sales Account","G/L Inventory Account"]
        writer.writerow(headers)
        
        # Write product data
        for product in products:
            if product.property_account_income_id.code and product.property_account_expense_id.code:
                writer.writerow([
                    product.default_code or '',  # Internal Reference may be empty
                    product.name,
                    product_categ_dictionary.get(product.detailed_type,0),
                    f"{product.list_price:.2f}",  # Sales Price formatted to 2 decimal places
                    f"{product.standard_price:.2f}",  # Cost formatted to 2 decimal places
                    product.property_account_income_id.code.replace(".","-"),
                    product.property_account_expense_id.code.replace(".","-"),

                ])
        
        # Move to beginning of the file
        output.seek(0)
        csv_data = output.getvalue()
        output.close()
        return csv_data

