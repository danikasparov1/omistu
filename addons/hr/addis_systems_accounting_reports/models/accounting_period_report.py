from odoo import api, fields, models

class AddissystemsAccountCommonReport(models.TransientModel):
    _inherit="account.common.report"
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

class AddissystemsAccountTaxReport(models.TransientModel):
    _inherit="account.tax.report.wizard"
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
        if self.filter_by_period:
            for record in self:
                record.period_from = None
                record.period_to = None

class AddissystemsAccountDayBookReport(models.TransientModel):
    _inherit="account.daybook.report"
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

    @api.onchange('period_from')
    def _onchange_period_from(self):
        for record in self:
            record.date_from = record.period_from.date_from

    @api.onchange('period_to')
    def _onchange_period_to(self):
        for record in self:
            record.date_to = record.period_to.date_to

   

class AddissystemsAccountCashBookReport(models.TransientModel):
    _inherit="account.cashbook.report"
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
    
class AddissystemsAccountBankBookReport(models.TransientModel):
    _inherit="account.bankbook.report"
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
    

class AddissystemsAccountAgedTrialBalance(models.TransientModel):
    _inherit="account.aged.trial.balance"
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