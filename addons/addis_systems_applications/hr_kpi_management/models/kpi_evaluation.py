# models/kpi_evaluation.py
from odoo import models, fields, api

class KPIEvaluation(models.Model):
    _name = 'hr.kpi.evaluation'
    _description = 'KPI Evaluation'

    kpi_id = fields.Many2one('hr.kpi', string='KPI', required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    actual_value = fields.Float(string='Actual Performance')
    evaluation_date = fields.Date(string='Evaluation Date', default=fields.Date.today)
    performance_score = fields.Float(string='Performance Score', compute='_compute_performance_score')

    @api.depends('actual_value', 'kpi_id')
    def _compute_performance_score(self):
        for record in self:
            if record.kpi_id.target_value:
                record.performance_score = (record.actual_value / record.kpi_id.target_value) * 100
            else:
                record.performance_score = 0