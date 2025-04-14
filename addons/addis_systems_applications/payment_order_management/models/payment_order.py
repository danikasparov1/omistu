# from odoo import models, fields, api
# from odoo.exceptions import UserError
# from datetime import date

# class PaymentOrder(models.Model):
#     _name = 'payment.order'
#     _description = 'Payment Order'

#     # Fields
#     payment_for = fields.Selection([
#         ('employee', 'Employee'),
#         ('supplier', 'Supplier'),
#         ('other', 'Other')
#     ], string="Payment For", required=True)
#     payment_reason = fields.Text("Payment Reason", required=True)
#     date = fields.Date("Date", default=fields.Date.context_today, required=True)
#     amount = fields.Float("Amount", required=True)
#     tax = fields.Float("Tax", required=False, help="Applicable tax on the amount.")
#     withholding = fields.Float("Withholding", required=False, help="Applicable withholding on the amount.")
#     total_amount = fields.Float("Total Amount", compute="_compute_total_amount", store=True)
#     debit_account_id = fields.Many2one('account.account', string="Debit Account", required=True, 
#                                        domain=[('user_type_id.type', '=', 'liquidity')], 
#                                        help="Select the account for debiting the payment.")
#     journal_id = fields.Many2one('account.journal', string="Journal", required=True, 
#                                  domain=[('type', '=', 'bank')], 
#                                  help="Select the journal for this payment order.")

#     # Computed Field for Total Amount after Tax and Withholding
#     @api.depends('amount', 'tax', 'withholding')
#     def _compute_total_amount(self):
#         for record in self:
#             record.total_amount = record.amount + (record.tax or 0.0) - (record.withholding or 0.0)

#     # Create Accounting Journal Entry for the Payment Order
#     def action_create_journal_entry(self):
#         for record in self:
#             if record.total_amount <= 0:
#                 raise UserError("The total payment amount must be greater than zero.")
#             if not record.journal_id:
#                 raise UserError("Please select a journal for this payment order.")

#             # Get the Accounts Payable (A/P) account
#             ap_account = self.env['account.account'].search([('user_type_id.type', '=', 'payable')], limit=1)
#             if not ap_account:
#                 raise UserError("Accounts Payable account not found. Please configure it.")

#             # Create journal entry lines
#             move_line_vals = [
#                 {
#                     'account_id': ap_account.id,
#                     'name': record.payment_reason,
#                     'credit': record.total_amount,
#                 },
#                 {
#                     'account_id': record.debit_account_id.id,
#                     'name': record.payment_reason,
#                     'debit': record.total_amount,
#                 }
#             ]

#             # Create the journal entry
#             move_vals = {
#                 'journal_id': record.journal_id.id,
#                 'date': record.date,
#                 'ref': f'Payment for {record.payment_for} - {record.payment_reason}',
#                 'line_ids': [(0, 0, line) for line in move_line_vals],
#             }
#             move = self.env['account.move'].create(move_vals)
#             move.action_post()  # Post the journal entry to make it effective


from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import date

class PaymentOrder(models.Model):
    _name = 'payment.order'
    _description = 'Payment Order'

    # Fields
    payment_for = fields.Selection([
        ('employee', 'Employee'),
        ('supplier', 'Supplier'),
        ('other', 'Other')
    ], string="Payment For", required=True)
    payment_reason = fields.Text("Payment Reason", required=True)
    date = fields.Date("Date", default=fields.Date.context_today, required=True)
    amount = fields.Float("Amount", required=True)
    tax = fields.Float("Tax", required=False, help="Applicable tax on the amount.")
    withholding = fields.Float("Withholding", required=False, help="Applicable withholding on the amount.")
    total_amount = fields.Float("Total Amount", compute="_compute_total_amount", store=True)
    debit_account_id = fields.Many2one('account.account', string="Debit Account", required=True, 
                                       domain=[('user_type_id.type', '=', 'liquidity')], 
                                       help="Select the account for debiting the payment.")
    journal_id = fields.Many2one('account.journal', string="Journal", required=True, 
                                 domain=[('type', '=', 'bank')], 
                                 help="Select the journal for this payment order.")
    
    # State field to track the status of the payment order
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('cancelled', 'Cancelled'),
    ], default='draft', string='State', required=True)

    # Computed Field for Total Amount after Tax and Withholding
    @api.depends('amount', 'tax', 'withholding')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = record.amount + (record.tax or 0.0) - (record.withholding or 0.0)

    # Create Accounting Journal Entry for the Payment Order
    def action_create_journal_entry(self):
        for record in self:
            if record.state != 'draft':  # Ensure the payment is in draft state
                raise UserError("You can only create a journal entry for payments in the 'Draft' state.")

            if record.total_amount <= 0:
                raise UserError("The total payment amount must be greater than zero.")
            if not record.journal_id:
                raise UserError("Please select a journal for this payment order.")
            if not record.debit_account_id:
                raise UserError("Please select a debit account for this payment order.")

            # Get the Accounts Payable (A/P) account
            ap_account = self.env['account.account'].search([('user_type_id.type', '=', 'payable')], limit=1)
            if not ap_account:
                raise UserError("Accounts Payable account not found. Please configure it.")

            # Create journal entry lines
            move_line_vals = [
                {
                    'account_id': ap_account.id,
                    'name': record.payment_reason,
                    'credit': record.total_amount,
                },
                {
                    'account_id': record.debit_account_id.id,
                    'name': record.payment_reason,
                    'debit': record.total_amount,
                }
            ]

            # Create the journal entry
            move_vals = {
                'journal_id': record.journal_id.id,
                'date': record.date,
                'ref': f'Payment for {record.payment_for} - {record.payment_reason}',
                'line_ids': [(0, 0, line) for line in move_line_vals],
            }
            move = self.env['account.move'].create(move_vals)
            move.action_post()  # Post the journal entry to make it effective

            # Update the state to 'posted' after successful journal entry creation
            record.state = 'posted'

    # Action to cancel the payment order
    def action_cancel(self):
        for record in self:
            if record.state != 'draft':  # Only allow cancellation in draft state
                raise UserError("You can only cancel payment orders in 'Draft' state.")
            record.state = 'cancelled'
