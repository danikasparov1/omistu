from odoo import models, fields

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    is_committee = fields.Boolean(string="Is Committee", help="Check if the employee is a committee member")
class TenderLineEvaluation(models.Model):
    _inherit = "tender.line.evaluation"

    employee_id = fields.Many2one("hr.employee", string="Employee")
from odoo import models, fields

class ResUsers(models.Model):
    _inherit = "res.users"

    is_committee = fields.Boolean(string="Is Committee")
