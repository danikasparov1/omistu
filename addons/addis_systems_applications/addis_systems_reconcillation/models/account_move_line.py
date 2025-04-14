from odoo import fields, models, api, tools, _, SUPERUSER_ID
from odoo.exceptions import ValidationError, AccessError, UserError

class AddisSystemsAccountMoveLine(models.Model):
    _inherit = "account.move.line"
    bank_statement_with = fields.Many2one(string="Bank statement",comodel_name="account.bank.statement")
    addis_is_reconciled = fields.Boolean(default=False,string="Is Reconciled")

    def action_addis_open_move(self):
        for record in self:
        # Perform actions for each record if necessary
            return {
                'name': 'Journal Entry',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'views': [(False, 'form')],
                'res_model': 'account.move',
                'res_id': record.move_id.id,
                'target': 'current',
            }
        
    @api.model
    def addisystems_reconcile(self, statement_id=False, selectedids=[]):
        self = self.browse(selectedids)
        bank_statement = self.env['account.bank.statement'].browse(statement_id)
        for record in self:
            if record.addis_is_reconciled :
                raise ValidationError("There are already reconciled entries")
            
            if record.parent_state !='posted':
                raise ValidationError("Only Posted Entries can be reconciled")
            record.addis_is_reconciled = True
            record.bank_statement_with=bank_statement
           
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }