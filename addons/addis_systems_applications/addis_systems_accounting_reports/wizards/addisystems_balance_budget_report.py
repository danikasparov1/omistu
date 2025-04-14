from odoo import fields, models, api, _
from odoo.exceptions import UserError

class AddissystemsAccountBalanceReport(models.TransientModel):
    _name="addisystems.balance.budget.report"
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True, default=lambda self: self.env.company)
    journal_ids = fields.Many2many(
        comodel_name='account.journal',
        string='Journals',
        required=True,
        default=lambda self: self.env['account.journal'].search([('company_id', '=', self.company_id.id)]),
        domain="[('company_id', '=', company_id)]",
    )
    target_move = fields.Selection([('posted', 'All Posted Entries'),
                                    (' ', 'All Entries'),
                                    ], string='Target Moves', required=True, default='posted')
    filter_by_period = fields.Boolean(string="Filter by Period", default=True)
    period_from = fields.Many2one('account.fiscal.year', string="Fiscal Year", )
    period_to = fields.Many2one('account.fiscal.year', string="Fiscal Year", )
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')

    @api.onchange('period_from')
    def _onchange_period_from(self):
        for record in self:
            if record.period_from:
                record.date_from = record.period_from.date_from

    @api.onchange('period_to')
    def _onchange_period_to(self):
        for record in self:
            if record.period_to:
                record.date_to = record.period_to.date_to

    @api.onchange('filter_by_period')
    def _onchange_date_from(self):
            for record in self:
                 if not record.filter_by_period:
                    record.period_from = None
                    record.period_to = None

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id:
            self.journal_ids = self.env['account.journal'].search(
                [('company_id', '=', self.company_id.id)])
        else:
            self.journal_ids = self.env['account.journal'].search([])

    def get_constant_domain(self):
        domain=[]
        if self.target_move.strip():
            domain+=[("parent_state","=",self.target_move)]
        if self.date_from:
            domain+=[("date",">=",self.date_from)]
        if self.date_to:
            domain+=[("date","<=",self.date_to)] 
        if self.journal_ids:
            domain+=[("journal_id",'in',self.journal_ids.ids)]
        return domain
    
    def get_accounts(self,categ):
        domain= self.get_constant_domain()
        domain+=[('account_id.account_type', 'ilike', f'{categ}%')]
        return self.env["account.move.line"].search(domain).account_id
    
    def get_balance(self,account_id):
        domain= self.get_constant_domain()
        domain+=[('account_id.id', '=', f'{account_id}')]
        recs=self.env["account.move.line"].search(domain)
        return sum([jrn.balance for jrn in recs])
    
    def get_budget(self,account_id):
        domain=[('addissystems_account_budget_id.state','=','confirm')]
        if self.date_from:
            domain+=[("date_from",">=",self.date_from)]
        if self.date_to:
            domain+=[("date_to","<=",self.date_to)] 
        domain+=[('account_id.id', '=', f'{account_id}')]
        recs=self.env["addissystems.account.budget.line"].search(domain)
        return sum([jrn.amount for jrn in recs])
        
  
    def check_report(self):
        return self.env.ref("addis_systems_accounting_reports.addis_systems_balance_budget_report").report_action(self)
  
