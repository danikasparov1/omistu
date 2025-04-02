from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime, date
import calendar

class AddissystemsAccountIncomeStatementReport(models.TransientModel):
    _name="addisystems.income.statement.report"
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
    show_budget= fields.Boolean(string="show budget",default=False)
    twelve_periods = fields.Boolean(string="with 12 perods",default=False)
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
    def get_constant_domain_month(self):
        domain=[]
        today = datetime.today()
        first_day = date(today.year, today.month, 1)
        last_day = date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
        if self.target_move.strip():
            domain+=[("parent_state","=",self.target_move)]
        if self.date_from:
            domain+=[("date",">=",first_day)]
        if self.date_to:
            domain+=[("date","<=",last_day)] 
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
        return sum([-1*jrn.balance for jrn in recs])
    
    def get_balance_month(self,account_id):
        domain= self.get_constant_domain_month()
        domain+=[('account_id.id', '=', f'{account_id}')]
        recs=self.env["account.move.line"].search(domain)
        return sum([-1*jrn.balance for jrn in recs])
    
    def get_total_budget(self,account_id):
        domain=[('addissystems_account_budget_id.state','=','confirm')]
        if self.date_from:
            domain+=[("date_from",">=",self.date_from)]
        if self.date_to:
            domain+=[("date_to","<=",self.date_to)] 
        domain+=[('account_id.id', '=', f'{account_id}')]
        recs=self.env["addissystems.account.budget.line"].search(domain)
        return sum([jrn.amount for jrn in recs])
    
    def get_current_month_budget(self,account_id):
        domain=[('addissystems_account_budget_id.state','=','confirm')]
        today = datetime.today()
        first_day = date(today.year, today.month, 1)
        last_day = date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
        domain+=[("date_from",">=",first_day)]
        domain+=[("date_to","<=",last_day)] 
        domain+=[('account_id.id', '=', f'{account_id}')]
        recs=self.env["addissystems.account.budget.line"].search(domain)
        return sum([jrn.amount for jrn in recs])
    

    def check_report(self):
        return self.env.ref("addis_systems_accounting_reports.addis_systems_income_statement_summary_report").report_action(self)
  

    def get_constant_domain_twelve_period(self,period_idx):
        periods = self.env['account.fiscal.year'].search([], order="date_from asc")
        domain = []
        try:
            per=periods[period_idx-1]
        except:
            return False
        domain+=[("date",">=",per.date_from),("date","<=",per.date_to)]
        if self.journal_ids:
            domain+=[("journal_id",'in',self.journal_ids.ids)]
        if self.target_move.strip():
            domain+=[("parent_state","=",self.target_move)]
        return domain

    def get_balance_with_period(self,account_id,period_idx):
        domain=self.get_constant_domain_twelve_period(period_idx=period_idx)
        if not domain:
            return 'N/A'
        domain+=[('account_id.id', '=', f'{account_id}')]
        recs=self.env["account.move.line"].search(domain)
        return sum([-1*jrn.balance for jrn in recs])
    
    def get_balance_under_category(self,categ,period_idx):
        domain=self.get_constant_domain_twelve_period(period_idx=period_idx)
        if not domain:
            return 'N/A'
        domain+=[('account_id.account_type', 'ilike', f'{categ}%')]
        recs=self.env["account.move.line"].search(domain)
        return sum([-1*jrn.balance for jrn in recs])
    def get_net_income_balance_twelve_period(self,period_idx):
        try:
            diffe=self.get_balance_under_category(categ='income',period_idx=period_idx) - self.get_balance_under_category(categ='expense',period_idx=period_idx)
        except:
            return 'N/A'
        return diffe
    def check_report_twelve_period(self):
        return self.env.ref("addis_systems_accounting_reports.addis_systems_income_statement_twelve_periods_summary_report").report_action(self)
  
