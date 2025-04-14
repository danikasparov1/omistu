from odoo import models, fields, api

class ManufacturingOrder(models.Model):
    _inherit = 'mrp.production'

    branch_id = fields.Many2one('res.branch', string='Branch', required=True, default=lambda self: self.env.user.default_branch_id)

    @api.model
    def create(self, vals):
        if 'branch_id' not in vals:
            vals['branch_id'] = self.env.user.default_branch_id.id
        return super(ManufacturingOrder, self).create(vals)
