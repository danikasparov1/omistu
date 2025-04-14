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

coa_dict = {
    'asset_receivable': 'Accounts Receivable',
    'asset_cash': 'Cash',
    'asset_current': 'Other Current Assets',
    'asset_non_current': 'Long Term Liabilities',
    'asset_prepayments': 'Prepayments',
    'asset_fixed': 'Fixed Assets',
    'liability_payable': 'Accounts Payable',
    'liability_credit_card': 'Credit Card',
    'liability_current': 'Other Current Liabilities',
    'liability_non_current': 'Non-current Liabilities',
    'equity': 'Equity-gets closed',
    'equity_unaffected': 'Equity-Retained Earnings',
    'income': 'Income',
    'income_other': 'Other Income',
    'expense': 'Expenses',
    'expense_depreciation': 'Accumulated Depreciation',
    'expense_direct_cost': 'Cost of Sales',
    'off_balance': 'Off-Balance Sheet',
}


class CoaPeachtree(http.Controller):
    @http.route(['/web/coapeachtree/download'],type='http', auth="user")
    def download_coa_peachtree(self, account_ids=None, **kwargs):
        if account_ids:
            account_ids = list(filter(None, (int(mid) for mid in account_ids.split(',') if mid.isdigit())))
            token = generate_token()
            aa = self.get_csv_data(request.env['account.account'].browse(account_ids))
            file_name = "accounts"
            response = request.make_response(
                aa,
                headers=[
                    ('Content-Type', 'text/csv'),
                    ('Content-Disposition', content_disposition(f"{file_name}.csv"))
                ]
            )
            response.set_cookie('fileToken', token)
            return response

    def get_csv_data(self, accounts):
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Determine the header based on account type
        headers = ['GL AccountID','Account Description' , "Account Type",'inactive']

        # Write the header row
        writer.writerow(headers)
        
        # Write data rows
        for account in accounts:
            writer.writerow([str(account.code), account.name,coa_dict[account.account_type] , False])    
        output.seek(0)
        return output.getvalue()

