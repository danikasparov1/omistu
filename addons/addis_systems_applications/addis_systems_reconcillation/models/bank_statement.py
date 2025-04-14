from odoo import fields, models, api, tools, _, SUPERUSER_ID
from odoo.exceptions import ValidationError, AccessError, UserError

class AddisSystemsBankStatement(models.Model):
    _name = "addissystems.bank.statement"
    _description = "Addissystems Bank Statement"
    _check_company_auto = True

    name = fields.Char(
        string='Reference',
    )
    date = fields.Date( 
 
    )
    balance_start = fields.Monetary(
        string='Starting Balance',
    )

    balance_end = fields.Monetary(
        string='Ending Balance',
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        compute='_compute_currency_id',
    )
    journal_id = fields.Many2one(
        comodel_name='account.journal',
        check_company=True,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        related='journal_id.company_id', store=True,
    )
    move_line_ids = fields.One2many(
        'account.move.line',
        'bank_statement_with',
        string='Journal Items',
        copy=True,
    )
    interest_income_account = fields.Many2one('account.account',string="Interest Income Account")
    interest_income_amount = fields.Monetary(string="Interest Amount")
    service_charge_account = fields.Many2one('account.account',string="Service Charge Account")
    service_charge_amount = fields.Monetary(string="Service Charge Amount")

    @api.depends('journal_id')
    def _compute_currency_id(self):
        for statement in self:
            statement.currency_id = statement.journal_id.currency_id or statement.company_id.currency_id

    @api.model
    def get_reconciled_amount(self,active_id):
        bank_state=self.browse(active_id)
        domain=[('account_id',"=",bank_state.journal_id.default_account_id.id),("addis_is_reconciled","=",True)]
        lines = self.env['account.move.line'].search(domain)
        return sum([line.balance for line in lines])
    
    @api.model
    def get_un_reconciled_amount(self,active_id):
        bank_state=self.browse(active_id)
        domain=[('account_id',"=",bank_state.journal_id.default_account_id.id),("addis_is_reconciled","=",False)]
        lines = self.env['account.move.line'].search(domain)
        return sum([line.balance for line in lines])


