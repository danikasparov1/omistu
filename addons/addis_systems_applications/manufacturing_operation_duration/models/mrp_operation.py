from odoo import models, fields, api

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    duration_expected_hours = fields.Float(
        string="Expected Duration (Hours)",
        compute="_compute_duration_hours",
        inverse="_set_duration_hours",
        store=True
    )

    @api.depends('duration_expected')
    def _compute_duration_hours(self):
        """Convert duration from minutes to hours."""
        for record in self:
            record.duration_expected_hours = record.duration_expected / 60 if record.duration_expected else 0

    def _set_duration_hours(self):
        """Convert duration from hours to minutes."""
        for record in self:
            record.duration_expected = record.duration_expected_hours * 60 if record.duration_expected_hours else 0
