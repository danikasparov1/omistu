from odoo import models, fields, api

class WorkOrder(models.Model):
    _inherit = 'mrp.workorder'

    branch_id = fields.Many2one(
        'res.branch', 
        string="Branch", 
        default=lambda self: self.env.user.branch_id,
        required=True
    )
