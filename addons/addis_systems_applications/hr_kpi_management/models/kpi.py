# models/kpi.py
from odoo import models, fields

class KPI(models.Model):
    _name = 'hr.kpi'
    _description = 'Key Performance Indicator'

    name = fields.Char(string='KPI Name', required=True)
    description = fields.Text(string='Description')
    kpi_type = fields.Selection([
        ('quantitative', 'Quantitative'),
        ('qualitative', 'Qualitative')
    ], string='KPI Type', required=True)
    measurement_unit = fields.Char(string='Measurement Unit')
    target_value = fields.Float(string='Target Value')
    frequency = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly')
    ], string='Evaluation Frequency', required=True)
