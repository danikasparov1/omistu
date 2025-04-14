from odoo import api, fields, models, _, Command
from odoo.tools.misc import formatLang

class AccountTaxInherited(models.Model):
    _inherit="account.tax"
    def compute_all(self, price_unit, currency=None, quantity=1.0, product=None, partner=None, is_refund=False, handle_price_include=True, include_caba_tags=False, fixed_multiplicator=1):
        returned_data=super().compute_all(price_unit, currency=currency, quantity=quantity, product=product, partner=partner, is_refund=is_refund, handle_price_include=handle_price_include, include_caba_tags=include_caba_tags, fixed_multiplicator=fixed_multiplicator)
        
        for tax in returned_data["taxes"]:
            if tax["amount"]<0:
                returned_data["total_included"]-=tax["amount"]
        return returned_data
    
    
class AccountMoveInherited(models.Model):
    _inherit="account.move"
    amount_withholding = fields.Monetary(
        string='Tax Signed',
        compute='_compute_amount', store=True, readonly=True,
        currency_field='company_currency_id',)
    
    @api.depends(
        'line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.balance',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'line_ids.full_reconcile_id',
        'state')
    def _compute_amount(self):
        returned_data=super()._compute_amount()
        for move in self:
            total=move.amount_total_signed
            total_tax=move.amount_tax_signed
            total_withholding=0
            for line in move.line_ids:
                if line.display_type == 'tax' or (line.display_type == 'rounding' and line.tax_repartition_line_id):
                    if line.balance >0:
                        total_withholding+=line.balance
                        total+= line.balance
                        total_tax += line.balance
            move.amount_total_signed= total
            move.amount_tax_signed=total_tax
            move.amount_withholding=total_withholding
            #move.amount_total_in_currency_signed =total

    @api.depends_context('lang')
    @api.depends(
        'invoice_line_ids.currency_rate',
        'invoice_line_ids.tax_base_amount',
        'invoice_line_ids.tax_line_id',
        'invoice_line_ids.price_total',
        'invoice_line_ids.price_subtotal',
        'invoice_payment_term_id',
        'partner_id',
        'currency_id',
    )
    def _compute_tax_totals(self):
        x=super()._compute_tax_totals()
        tax_totals = self.tax_totals
        if tax_totals and tax_totals["groups_by_subtotal"] and tax_totals["groups_by_subtotal"]["Untaxed Amount"]:
            for tax in tax_totals["groups_by_subtotal"]["Untaxed Amount"]:
                if tax["tax_group_amount"]<0:
                    tax_totals["amount_total"] -= tax["tax_group_amount"]
                    tax_totals["formatted_amount_total"]=formatLang(self.env, tax_totals['amount_total'], currency_obj=self.currency_id)
        self.tax_totals=tax_totals

                    

