from odoo import models, fields, api
from odoo.exceptions import ValidationError

class PaymentOrder(models.Model):
    _name = 'payment.order'
    _description = 'Payment Order'

    payment_for = fields.Selection(
        [('employee', 'Employee'), ('supplier', 'Supplier'), ('other', 'Other')],
        string="Payment For",
        required=True
    )
    payment_reason = fields.Text(string="Payment Reason", required=True)
    date = fields.Date(string="Date", default=fields.Date.context_today, required=True)
    amount = fields.Float(string="Amount", required=True)
    tax = fields.Float(string="Tax (%)", default=0.0)
    withholding = fields.Float(string="Withholding (%)", default=0.0)
    total_amount = fields.Float(string="Total Amount", compute='_compute_total_amount', store=True)
    debit_account_id = fields.Many2one(
        'account.account',
        string="Debit Account",
        domain="[('account_type', '=', 'asset_cash')]",  # Updated for Odoo 17
        # required=True
    )
    journal_id = fields.Many2one('account.journal', string="Journal")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], default='draft', string='Status')

    def action_cancel(self):

        self.state = 'cancelled'

    
    def action_approve(self):

        self.state = 'approved'

    
    def action_pay(self):



            self.state = 'done'

    # def action_pay(self):
    #     for record in self:
    #         record.create_journal_entry()  # Create the journal entry
    #         record.state = 'done'  # Change state to 'done'


    @api.depends('amount', 'tax', 'withholding')
    def _compute_total_amount(self):
        for record in self:
            tax_amount = (record.amount * record.tax) / 100
            withholding_amount = (record.amount * record.withholding) / 100
            record.total_amount = record.amount + tax_amount - withholding_amount


    def create_journal_entry(self):
        for record in self:
            if record.total_amount <= 0:
                raise ValidationError("The total amount must be greater than zero.")

            # Find a payable account
            payable_account = self.env['account.account'].search(
                [('account_type', '=', 'liability_payable')],
                limit=1
            )
            if not payable_account:
                raise ValidationError("No payable account found. Please configure a payable account.")

            move_vals = {
                'journal_id': record.journal_id.id,
                'date': record.date,
                'line_ids': [
                    (0, 0, {
                        'account_id': record.debit_account_id.id,
                        'debit': record.total_amount,
                        'credit': 0.0,
                    }),
                    (0, 0, {
                        'account_id': payable_account.id,
                        'debit': 0.0,
                        'credit': record.total_amount,
                    })
                ]
            }
            move = self.env['account.move'].create(move_vals)
            move.action_post()  # Updated to use action_post() in Odoo 17
