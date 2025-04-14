from odoo import models, fields, api

class ManufacturingOrder(models.Model):
    _inherit = 'mrp.production'

    branch_id = fields.Many2one('res.company', string='Branch', required=True, readonly=True)
    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id:
            self.branch_id = self.company_id
from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    branch_id = fields.Many2one('res.company', string="Branch")