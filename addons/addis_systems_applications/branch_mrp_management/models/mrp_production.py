from odoo import models, fields, api

class ManufacturingOrder(models.Model):
    _inherit = 'mrp.production'

    branch_id = fields.Many2one(
        'res.branch', 
        string="Branch", 
        default=lambda self: self.env.user.branch_id,
        required=True
    )

class ResUsers(models.Model):
    _inherit = 'res.users'

    # branch_id = fields.Many2one('res.branch', string="Branch")
    branch_id = fields.Char()

    
    