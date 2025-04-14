from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero
from odoo.models import NewId

class AccountPaymentInherited(models.Model):
    _inherit = "account.payment"

    tax_ids = fields.Many2many(
        comodel_name='account.tax',
        string="Taxes",
        store=True,
        readonly=False,
        context={'active_test': False},
        check_company=True,
        tracking=True,
    )
    payment_taxed_amount = fields.Monetary(currency_field='currency_id',compute="get_tax_total")
    expense_account_id = fields.Many2one('account.account',string="Payment Debit/credit Account")
    is_not_saved = fields.Boolean(compute="compute_is_saved")

    @api.depends('tax_ids','amount')
    def compute_is_saved(self):
        self.is_not_saved= isinstance(self.move_id.id, NewId)
        

    @api.depends('tax_ids','amount')
    def get_tax_total(self):
        if self.tax_ids:
            tax_details = self.tax_ids.compute_all(self.amount)
            tax_amount = sum(t['amount'] for t in tax_details['taxes'])
            self.payment_taxed_amount = tax_amount
        else:
            self.payment_taxed_amount = 0

    @api.model
    def _get_trigger_fields_to_synchronize(self):
        return (
            'date', 'amount', 'tax_ids','payment_type', 'partner_type', 'payment_reference', 'is_internal_transfer',
            'currency_id', 'partner_id', 'destination_account_id', 'partner_bank_id', 'journal_id'
        )
    

    def _prepare_move_line_default_vals(self, write_off_line_vals=None, force_balance=None):
        """
        Prepare move line values without calling super and using expense_account_id to replace default accounts.
        """
        self.ensure_one()
        if not self.tax_ids:
            return super()._prepare_move_line_default_vals()
        

        # Validate required accounts
        if not self.expense_account_id:
            raise UserError(_("Please configure an Expense Account for this payment."))

        if not self.outstanding_account_id:
            raise UserError(_(
                "You can't create a new payment without an outstanding payments/receipts account set either on the company "
                "or the %s payment method in the %s journal.",
                self.payment_method_line_id.name, self.journal_id.display_name
            ))

        # Compute amounts
        tax_amount = 0
        if self.tax_ids:
            tax_details = self.tax_ids.compute_all(self.amount)
            tax_amount = sum(t['amount'] for t in tax_details['taxes'])

        if self.payment_type == 'inbound':
            # Receiving money
            liquidity_amount_currency = self.amount
            counterpart_amount_currency = -(self.amount + tax_amount)
        elif self.payment_type == 'outbound':
            # Sending money
            liquidity_amount_currency = -self.amount
            counterpart_amount_currency = self.amount + tax_amount
        else:
            liquidity_amount_currency = 0.0
            counterpart_amount_currency = 0.0

        currency_id = self.currency_id.id
        liquidity_balance = self.currency_id._convert(
            liquidity_amount_currency,
            self.company_id.currency_id,
            self.company_id,
            self.date,
        )
        counterpart_balance = self.currency_id._convert(
            counterpart_amount_currency,
            self.company_id.currency_id,
            self.company_id,
            self.date,
        )
        total_tax_balance = self.currency_id._convert(
            tax_amount,
            self.company_id.currency_id,
            self.company_id,
            self.date,
        )
        liquidity_line_name = ''.join(x[1] for x in self._get_liquidity_aml_display_name_list())
        counterpart_line_name = ''.join(x[1] for x in self._get_counterpart_aml_display_name_list())
        # Move lines
        move_lines = [
            # Liquidity line
            {
                'name': liquidity_line_name,
                'date_maturity': self.date,
                'amount_currency': liquidity_amount_currency,
                'currency_id': currency_id,
                'debit': liquidity_balance if liquidity_balance > 0 else 0.0,
                'credit': -liquidity_balance if liquidity_balance < 0 else 0.0,
                'partner_id': self.partner_id.id,
                'account_id': self.outstanding_account_id.id,
            },
            # Counterpart line
            {
                'name': counterpart_line_name,
                'date_maturity': self.date,
                'amount_currency': counterpart_amount_currency,
                'currency_id': currency_id,
                'debit': counterpart_balance if counterpart_balance > 0 else 0.0,
                'credit': -counterpart_balance if counterpart_balance < 0 else 0.0,
                'partner_id': self.partner_id.id,
                'account_id': self.expense_account_id.id,  # Using the new expense_account_id
            },
        ]
      
        if self.tax_ids:
            for tax in self.tax_ids:
                tax_account_id = tax.account_payment_id.id
                tax_amount_single = tax.compute_all(self.amount)
                tax_amount_single=sum(t['amount'] for t in tax_amount_single['taxes'])
                if not tax_account_id:
                    raise UserError(
                        _("Tax '%s' does not have an associated account. Please configure it properly.") % tax.name
                    )
                move_lines.insert(-1,{
                    'account_id': tax_account_id,
                    'debit': tax_amount_single if self.payment_type == 'inbound' else 0,
                    'credit': tax_amount_single if self.payment_type == 'outbound' else 0,
                    'name': _('Tax: %s') % tax.name,
                    'partner_id': self.partner_id.id,
                })

        total_debit = sum(line['debit'] for line in move_lines)
        total_credit = sum(line['credit'] for line in move_lines)
        if not float_is_zero(total_debit - total_credit, precision_digits=self.currency_id.decimal_places):
            raise UserError(_("The journal entry is not balanced. Please check the configuration."))
        
        return move_lines
    

  