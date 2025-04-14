from odoo import models, fields, api

class CarWeight(models.Model):
    _name = 'car.weight'
    _description = 'Car Weight Tracking'

    name = fields.Char(string='Car Reference', required=True)
    entry_weight = fields.Float(string='Entry Weight (kg)', required=True)
    exit_weight = fields.Float(string='Exit Weight (kg)')
    soap_weight = fields.Float(string='Soap Product Weight (kg)', compute='_compute_soap_weight', store=True)
    entry_time = fields.Datetime(string='Entry Time', default=fields.Datetime.now, required=True)
    exit_time = fields.Datetime(string='Exit Time')

    @api.depends('entry_weight', 'exit_weight')
    def _compute_soap_weight(self):
        for record in self:
            if record.exit_weight:
                record.soap_weight = record.entry_weight - record.exit_weight
            else:
                record.soap_weight = 0.0