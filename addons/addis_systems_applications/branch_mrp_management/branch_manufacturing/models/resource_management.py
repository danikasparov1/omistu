from odoo import fields, models

from odoo import models, fields, api



class ResourceManagement(models.Model):
    _name = 'resource.management'
    _description = 'Resource Management for Branches'

    branch_id = fields.Many2one('res.branch', string='Branch')
    resource_type = fields.Selection([('equipment', 'Equipment'), ('labor', 'Labor')], string='Resource Type')
    available_quantity = fields.Integer(string='Available Quantity')



class BranchReport(models.Model):

    _name = 'branch.report'

    _description = 'Branch Report'



    branch_id = fields.Many2one('res.branch', string='Branch')

    production_volume = fields.Integer(string='Production Volume')

    operation_time = fields.Float(string='Operation Time')

    resource_utilization = fields.Float(string='Resource Utilization')