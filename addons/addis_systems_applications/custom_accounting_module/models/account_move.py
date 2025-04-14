from odoo import models, api, _
from odoo.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def _post(self, soft=True):
        for move in self:
            company = move.company_id
            business_type = company.business_type

            # Get necessary accounts
            account_ar = self.env['account.account'].search([('account_type', '=', 'receivable')], limit=1)
            account_income = self.env['account.account'].search([('account_type', '=', 'income')], limit=1)
            account_vat = self.env['account.account'].search([('code', '=', 'VAT')], limit=1)
            account_inventory = self.env['account.account'].search([('account_type', '=', 'stock')], limit=1)
            account_cogs = self.env['account.account'].search([('account_type', '=', 'expense')], limit=1)

            # Log the results of the search queries
            logger.info(f"Receivable account: {account_ar}")
            logger.info(f"Income account: {account_income}")
            logger.info(f"VAT account: {account_vat}")
            logger.info(f"Inventory account: {account_inventory}")
            logger.info(f"COGS account: {account_cogs}")

            # Validate that all required accounts are found
            if not account_ar:
                raise ValidationError(_("Receivable account not found."))
            if not account_income:
                raise ValidationError(_("Income account not found."))
            if not account_vat:
                raise ValidationError(_("VAT account not found."))
            if not account_inventory:
                raise ValidationError(_("Inventory account not found."))
            if not account_cogs:
                raise ValidationError(_("COGS account not found."))

            # Determine journal structure
            if business_type == 'service':
                move.line_ids = [
                    (0, 0, {
                        'account_id': account_ar.id,
                        'debit': move.amount_total,
                        'credit': 0,
                    }),
                    (0, 0, {
                        'account_id': account_income.id,
                        'debit': 0,
                        'credit': move.amount_total,
                    }),
                ]
            elif business_type == 'wholesale_retail':
                move.line_ids = [
                    (0, 0, {
                        'account_id': account_ar.id,
                        'debit': move.amount_total,
                        'credit': 0,
                    }),
                    (0, 0, {
                        'account_id': account_income.id,
                        'debit': 0,
                        'credit': move.amount_total,
                    }),
                    (0, 0, {
                        'account_id': account_vat.id,
                        'debit': move.amount_tax,
                        'credit': 0,
                    }),
                ]
            elif business_type == 'manufacturing':
                move.line_ids = [
                    (0, 0, {
                        'account_id': account_inventory.id,
                        'debit': move.amount_total,
                        'credit': 0,
                    }),
                    (0, 0, {
                        'account_id': account_cogs.id,
                        'debit': 0,
                        'credit': move.amount_total,
                    }),
                ]

        return super(AccountMove, self)._post(soft)
