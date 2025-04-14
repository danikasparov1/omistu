from odoo import fields, models, api, _
from odoo.exceptions import UserError

class AddissystemsAccountBalanceReport(models.TransientModel):
    _name="addisystems.account.reconcillation.report"
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True, default=lambda self: self.env.company)
    journal_bank_ids = fields.Many2one(
        comodel_name='account.journal',
        string='Bank',
        required=False,
        domain="[('company_id', '=', company_id),('type','=','bank')]",
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
    def get_constant_domain_coa(self):
        domain=[]
        if self.target_move.strip():
            domain+=[("parent_state","=",self.target_move)]
        if self.date_from:
            domain+=[("date",">=",self.date_from)]
        if self.date_to:
            domain+=[("date","<=",self.date_to)] 
        if self.journal_bank_ids:
            domain+=[("journal_id",'in',self.journal_bank_ids.ids)]
        return domain
    
    def get_balance_of_bank_account(self):
        domain=self.get_constant_domain_coa()
        domain+=[('account_id.id', '=', f'{self.journal_bank_ids.default_account_id.id}')]
        recs=self.env["account.move.line"].search(domain)
        return sum([jrn.balance for jrn in recs])
    
    def get_constant_domain_bank(self):
        domain=[]
        if self.date_from:
            domain+=[("date",">=",self.date_from)]
        if self.date_to:
            domain+=[("date","<=",self.date_to)] 
        if self.journal_bank_ids:
            domain+=[("journal_id",'in',self.journal_bank_ids.ids)]
        return domain
    
    def get_constant_domain_payment(self):
        domain=[]
        if self.date_from:
            domain+=[("date",">=",self.date_from)]
        if self.date_to:
            domain+=[("date","<=",self.date_to)] 
        if self.journal_bank_ids:
            domain+=[("journal_id",'in',self.journal_bank_ids.ids)]
        return domain
    
    def get_receipts_with_unreconcilled(self):
        domain=self.get_constant_domain_bank()
        domain+=[('amount','>',0)]
        return self.env["account.bank.statement.line"].search(domain)

    def get_total_receipts_with_unreconcilled(self):
        domain=self.get_constant_domain_bank()
        domain+=[('amount','>',0)]
        return sum([line.amount for line in self.env["account.bank.statement.line"].search(domain)])
    
    def get_total_payments_with_unreconcilled(self):
        domain=self.get_constant_domain_bank()
        domain+=[('amount','<',0)]
        return sum([line.amount for line in self.env["account.bank.statement.line"].search(domain)])
    
    def get_payments_with_unreconcilled(self):
        domain=self.get_constant_domain_bank()
        domain+=[('amount','<',0)]
        return self.env["account.bank.statement.line"].search(domain)
    
    def get_outstanding_receipts(self):
        domain=self.get_constant_domain_payment()
        domain+=[('payment_type','=','inbound'),('state','=','posted')]
        return self.env["account.payment"].search(domain)
    def get_total_outstanding_receipts(self):
        domain=self.get_constant_domain_payment()
        domain+=[('payment_type','=','inbound'),('state','=','posted')]
        return sum([line.amount for line in self.env["account.payment"].search(domain)])


    def get_outstanding_payments(self):
        domain=self.get_constant_domain_payment()
        domain+=[('payment_type','=','outbound'),('state','=','posted')]
        return self.env["account.payment"].search(domain)
    def get_total_outstanding_payments(self):
        domain=self.get_constant_domain_payment()
        domain+=[('payment_type','=','outbound'),('state','=','posted')]
        return sum([-1*line.amount for line in self.env["account.payment"].search(domain)])




    def get_total_bank_statement_debit(self):
        domain=[]
        if self.date_from:
            domain+=[('date','>=',self.date_from)]
        if self.date_to:
            domain+=[('date','<=',self.date_from)]
        return sum([stment.amount for stment in self.env['account.bank.statement.line'].search(domain) if stment.amount > 0])
    def get_total_bank_statement_credit(self):
        domain=[]
        if self.date_from:
            domain+=[('date','>=',self.date_from)]
        if self.date_to:
            domain+=[('date','<=',self.date_to)]
        return -1*sum([stment.amount for stment in self.env['account.bank.statement.line'].search(domain) if stment.amount < 0])

    def check_report(self):
        return self.env.ref("addis_systems_accounting_reports.addis_systems_account_reconcillation_report").report_action(self)
  
