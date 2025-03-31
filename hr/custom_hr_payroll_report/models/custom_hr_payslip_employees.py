from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class custom_hr_employee(models.TransientModel):
    _inherit = 'hr.payslip.employees'
    department_id = fields.Many2one('hr.department', string="Project")

    @api.model
    def default_get(self, fields_list):
        res = super(custom_hr_employee, self).default_get(fields_list)
        if 'project_id' in res:
            department_id = res['department_id']
            res['employee_ids'] = self.env['hr.employee'].search([('department_id', '=', department_id.id)]).ids
        return res

    @api.onchange('department_id')
    def _onchange_project_id(self):
        if self.department_id:
            employees=self.env['hr.employee'].search([('department_id', '=', self.department_id.id)]).ids
            if len(employees)>0:
                self.employee_ids = employees
            else:
                self.employee_ids=False
        else:
            self.employee_ids = self.env['hr.employee'].search([]).ids


