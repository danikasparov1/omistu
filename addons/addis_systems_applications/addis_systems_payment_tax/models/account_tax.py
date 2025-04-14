from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class AccountTaxInherited(models.Model):
    _inherit = "account.tax"
    account_payment_id = fields.Many2one('account.account',string="Payment Debit/credit Account")