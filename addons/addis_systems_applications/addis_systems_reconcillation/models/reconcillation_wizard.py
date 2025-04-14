from odoo import fields, models, api, tools, _, SUPERUSER_ID
from odoo.exceptions import ValidationError, AccessError, UserError
import ast

class AddissystemsReconcillationWizard(models.TransientModel):
    _name = "addisystems.reconcillation.wizard"
    _description = "Addisystems Reconcillation"
    bank_statement = fields.Many2one(string="Bank statement",comodel_name="addissystems.bank.statement")
    account_ids = fields.Many2one(string="Accounts",comodel_name="account.account")


    @api.onchange('bank_statement')
    def _onchange_bank_statement(self):
        if self.bank_statement:
            self.account_ids = self.bank_statement.journal_id.default_account_id
        else:
            self.account_ids = False

    def goto_reconcile(self):
        view_id= self.env.ref("addis_systems_reconcillation.addissystems_account_move_line_tree_reconcile_view").id 
        action = {
        'type': 'ir.actions.act_window',
        'name': 'Reconcile Accounts',
        'res_model': 'account.move.line',
        'views': [(view_id, 'tree')],  # Default tree view
        'domain':[("addis_is_reconciled",'=',False)],
        'context': {
            'search_view_ref': 'addis_systems_reconcillation.addissystems_account_move_line_search_reconcile_view',
            'search_default_account_id': self.account_ids.ids,
            'search_default_journal_id': self.bank_statement.journal_id.ids,
             'search_default_posted': 1,
        },
    }
        return action
    

    @api.model
    def get_bank_statement_info(self,active_d):
        record=self.browse(active_d)
        domain=[('display_type', 'not in', ('line_section', 'line_note')), ('parent_state', '!=', 'cancel'),('account_id','=',record.bank_statement.journal_id.default_account_id.id)]
        lines=self.env["account.move.line"].search(domain)
        balance=sum([line.balance for line in lines])
        data={
        "statement_id":record.bank_statement.id,
        "bank_name":record.bank_statement.journal_id.name,
        "account_balance":balance,
        "begining_balance":record.bank_statement.balance_start,
        "ending_balance":record.bank_statement.balance_end,
        "default_account_id":record.bank_statement.journal_id.default_account_id.display_name,
        "reconciled_amount":record.bank_statement.get_reconciled_amount(record.bank_statement.id),  
        "un_reconciled_amount":record.bank_statement.get_un_reconciled_amount(record.bank_statement.id)      
}
       
        return data



