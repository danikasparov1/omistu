from odoo import models, fields

class ManufacturingOperation(models.Model):
    _inherit = 'mrp.workorder'

    branch_id = fields.Many2one('branch', string='Branch', required=True)
