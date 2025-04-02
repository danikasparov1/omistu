# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountBudget(models.Model):
    _name = 'addissystems.account.budget'
    _description = 'Addisystems  Budget'
    _rec_name = 'name'
    name = fields.Char(string='Name', required=True)
    date_from = fields.Date(string='Start Date', required=True,
        help='Start Date, included in the fiscal year.')
    date_to = fields.Date(string='End Date', required=True,
        help='Ending Date, included in the fiscal year.')
    company_id = fields.Many2one('res.company', string='Company', required=True,
        default=lambda self: self.env.company)
    account_budget_line = fields.One2many(
        'addissystems.account.budget.line', 'addissystems_account_budget_id',
        'Budget Lines', copy=True
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ], 'Status', default='draft',)
    amount = fields.Float(string="Amount")

    def action_budget_confirm(self):
        self.write({'state': 'confirm'})
        lines_sum=sum([line.amount for line in self.account_budget_line])
        if lines_sum>self.amount:
            raise ValidationError(f"THe total budget is less than the sum of lines budget {lines_sum} > {self.amount}")
    def action_budget_draft(self):
        self.write({'state': 'draft'})
    @api.constrains('date_from', 'date_to', 'company_id')
    def _check_dates(self):
        '''
        Check interleaving between fiscal years.
        There are 3 cases to consider:

        s1   s2   e1   e2
        (    [----)----]

        s2   s1   e2   e1
        [----(----]    )

        s1   s2   e2   e1
        (    [----]    )
        '''
        for fy in self:
            # Starting date must be prior to the ending date
            date_from = fy.date_from
            date_to = fy.date_to
            if date_to < date_from:
                raise ValidationError(_('The ending date must not be prior to the starting date.'))
            domain = [
                ('id', '!=', fy.id),
                ('company_id', '=', fy.company_id.id),
                '|', '|',
                '&', ('date_from', '<=', fy.date_from), ('date_to', '>=', fy.date_from),
                '&', ('date_from', '<=', fy.date_to), ('date_to', '>=', fy.date_to),
                '&', ('date_from', '<=', fy.date_from), ('date_to', '>=', fy.date_to),
            ]
            if self.search_count(domain) > 0:
                raise ValidationError(_('You can not have an overlap between two Budget date ranges, '
                                        'please correct the start and/or end dates of your budgets.'))

class AccountBudgetLine(models.Model):
        _name = 'addissystems.account.budget.line'
        _description = "Addisystems Budget Line"
        addissystems_account_budget_id = fields.Many2one('addissystems.account.budget', 'Budget', ondelete='cascade', index=True, required=True)
        date_from = fields.Date('Start Date', related="addissystems_account_budget_id.date_from", required=True)
        date_to = fields.Date('End Date', related="addissystems_account_budget_id.date_to", required=True)
        account_id = fields.Many2one('account.account','Account')
        amount  = fields.Float(string="Amount")


