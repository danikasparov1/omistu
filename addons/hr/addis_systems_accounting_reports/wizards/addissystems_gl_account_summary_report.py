from odoo import fields, models, api, _
from odoo.exceptions import UserError

class AddissystemsAccountBalanceReport(models.TransientModel):
    _name="addisystems.glaccount.summary.report"
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
        domain=[('display_type', 'not in', ('line_section', 'line_note')), ('parent_state', '!=', 'cancel')]
        if self.target_move.strip():
            domain+=[("parent_state","=",self.target_move)]
        if self.date_from:
            domain+=[("date",">=",self.date_from)]
        if self.date_to:
            domain+=[("date","<=",self.date_to)] 
        if self.journal_ids:
            domain+=[("journal_id",'in',self.journal_ids.ids)]
        return domain
    
    def get_constant_domain_begining(self):
        domain=[('display_type', 'not in', ('line_section', 'line_note')), ('parent_state', '!=', 'cancel')]
        if self.target_move.strip():
            domain+=[("parent_state","=",self.target_move)]
        if self.date_to:
            domain+=[("date","<",self.date_from)] 
        if self.journal_ids:
            domain+=[("journal_id",'in',self.journal_ids.ids)]
        return domain
    
    def get_constant_domain_ending(self):
        domain=[('display_type', 'not in', ('line_section', 'line_note')), ('parent_state', '!=', 'cancel')]
        if self.target_move.strip():
            domain+=[("parent_state","=",self.target_move)]
        if self.date_to:
            domain+=[("date","<",self.date_to)] 
        if self.journal_ids:
            domain+=[("journal_id",'in',self.journal_ids.ids)]
        return domain
    
    

    def get_accounts(self):
        domain=self.get_constant_domain()
        lines = self.env["account.move.line"].search(domain)
        sorted_accounts = sorted(lines.mapped("account_id"), key=lambda acc: acc.code)
        return sorted_accounts
    

    def get_ending_balance(self,account_id):
        domain = self.get_constant_domain_ending()
        domain += [('account_id','=',account_id)]
        lines = self.env["account.move.line"].search(domain)
        total_balance=sum([line.balance for line in lines])
        return total_balance
    
    def get_begining_balance(self,account_id):
        if not self.date_from:
            account=self.env['account.account'].search([('id','=',account_id)])
            return account.opening_balance
        domain = self.get_constant_domain_begining()
        domain += [('account_id','=',account_id)]
        lines = self.env["account.move.line"].search(domain)
        total_balance=sum([line.balance for line in lines])
        return total_balance

    def get_debit_balance(self,account_id):
        domain = self.get_constant_domain()
        domain+=[('account_id.id', '=', f'{account_id}')]
        domain+=[('move_id','!=',self.env.company.account_opening_move_id.id)]
        recs=self.env["account.move.line"].search(domain)
        if self.env['account.account'].search([('id','=',account_id)]).code == '10200.00':
            for jrn in recs:
                print(jrn.name,jrn.move_id,self.env.company.account_opening_move_id.id,jrn.parent_state,jrn.display_type,jrn.debit,jrn.credit,jrn.balance)
        return sum([jrn.debit for jrn in recs])
    
    def get_credit_balance(self,account_id):
        domain= self.get_constant_domain()
        domain+=[('account_id.id', '=', f'{account_id}')]
        domain+=[('move_id','!=',self.env.company.account_opening_move_id.id)]
        recs=self.env["account.move.line"].search(domain)
        return sum([jrn.credit for jrn in recs])
    

    def get_balance(self,account_id):
        domain= self.get_constant_domain()
        domain+=[('account_id.id', '=', f'{account_id}')]
        domain+=[('move_id','!=',self.env.company.account_opening_move_id.id)]
        recs=self.env["account.move.line"].search(domain)
        return sum([jrn.balance for jrn in recs])

    def check_report(self):
        return self.env.ref("addis_systems_accounting_reports.addis_systems_gl_account_summary_report").report_action(self)
  
