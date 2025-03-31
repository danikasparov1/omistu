from odoo import models, fields, api, _
from datetime import datetime

class EarlyRetirement(models.Model):
   _name = "early.retirement"
   _inherit = ['mail.thread', 'mail.activity.mixin']

   employee_id = fields.Many2one('hr.employee',string="Employee")

   company_id=fields.Many2one('res.company',string="Hiring Compnay", related="employee_id.company_id")

   date_hired = fields.Date(compute="_compute_start_date", string="Date Hired")

   job_id = fields.Many2one('hr.job', related='employee_id.job_id')
   dept_id = fields.Many2one('hr.department', related="employee_id.department_id")
   date_of_birth = fields.Date( related='employee_id.birthday')
   state = fields.Selection(
      [('draft', 'Draft'), ('submit', 'Submitted'), ('approve', 'Approved')], default='draft',

   track_visibility='onchange')

   age = fields.Float(string="Age", compute="_employee_age")

   requested_date = fields.Date(string="Requested date")

   approved_by = fields.Many2one('hr.employee', string="Approved by")
   approved_date = fields.Date(string="Approved date")

   reason = fields.Text(string="Reason")

   attachement = fields.Binary(string="Attachement")

   def action_submit(self):
      self.state = 'submit'

   def action_approve(self):
      self.state = 'approve'

   @api.depends('employee_id')
   def _compute_start_date(self):
      recruited = self.env['hr.contract'].search(
         ['&', ('employee_id', '=', self.employee_id.id), ('state', '=', 'open')])
      self.date_hired = recruited.date_start

   # @api.depends('employee_id')
   # def _employee_age(self):
   #    for rec in self:
   #
   #       age = self.env['hr.employee'].search(
   #          [('id', '=', rec.employee_id.id)])
   #       rec.age = age.employee_age

   @api.model
   @api.depends('date_of_birth')
   def _employee_age(self):
      if self.date_of_birth:
         d2 = datetime.now().date()

         date_difference = d2.year - self.date_of_birth.year

         self.age = date_difference
      else:
         self.age = 0.0