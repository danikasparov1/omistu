from collections import defaultdict

from odoo import models, api,fields
from odoo.tools import float_is_zero, float_compare
from odoo.tools.misc import formatLang
default_debit_accounts = [
        "asset","expense"
    ]

class AccountMoveLineInherited(models.Model):
    _inherit="account.move.line"

    is_readonly = fields.Boolean(
        string="Readonly",
        compute="_compute_is_readonly",
        store=False  # Optional, make True if you want it stored
    )
    account_type = fields.Selection(
        related='account_id.account_type',
        string='Account Type',
        readonly=True,
        store=True,
        help="Type of the account associated with this move line."
    )
    
    @api.depends('debit','credit')
    def _compute_is_readonly(self):
        for line in self:
            if line.is_readonly:
                line.is_readonly = line.account_id.account_type.split("_")[0] not in default_debit_accounts
    def get_detail_lot(self):
        returned_data=[
        ]
        current_invoice_amls=self.sale_line_ids.invoice_lines.filtered(lambda aml: aml.move_id.state == 'posted').sorted(lambda aml: (aml.date, aml.move_name, aml.id))
        stock_move_lines = current_invoice_amls.sale_line_ids.move_ids.move_line_ids.filtered(lambda sml: sml.state == 'done' and sml.lot_id).sorted(lambda sml: (sml.date, sml.id))
        for sml in stock_move_lines:
            line_data={
                "name":f"{sml.product_id.name} [{sml.lot_id.name}][{sml.lot_id.expiration_date or ' '}]",
                "quantity":sml.product_uom_id._compute_quantity(sml.quantity, sml.product_id.uom_id)
            }
            returned_data.append(line_data)
        return returned_data
    
    class AccountMoveInherited(models.Model):
        _inherit="account.move"
        
        @api.model
        def custom_action(self):
            accouts_id = [line.account_id.id for line in self.env.company.account_opening_move_id.line_ids]
            accounts = self.env["account.account"].search([('id','not in',accouts_id),('deprecated', '=', False)])
            for account in accounts:
                self.env['account.move.line'].create({
                'move_id': self.env.company.account_opening_move_id.id,
                'account_id': account.id,
                'debit': 0.0,
                'credit': 0.0,
                'name': "Opening balance",  # Or any other appropriate value for the name field
            })
                
            return {
            'type': 'ir.actions.act_window',
            'name': 'Custom Form View',
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': self.env.company.account_opening_move_id.id,  # Opens the specified record
            'context': {'specific_view': True},
            'view_id': self.env.ref('addis_systems_accounting.inherit_view_move_begining_form').id,  # Reference to the form view ID
            'target': 'current',  # Opens in the same tab
        }
