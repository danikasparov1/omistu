from odoo import models, fields, api
from odoo.exceptions import ValidationError

class TechnicalValuationScores(models.Model):
    _name = 'technical.valuation.scores'
    _description = 'Technical Valuation Scores'

    criterion_id = fields.Many2one('tender.evaluation.criteria', string='Criterion', required=True)
    name = fields.Char(related="criterion_id.name", string="Criteria Title")
    assigned_target = fields.Float(related="criterion_id.weight", string='Assigned Target', required=True)
    actual_score = fields.Float(string='Actual Score')
    tender_id = fields.Many2one('tender.valuation.commute', string='Tender Valuation Commute', required=True)

    # Ensure that each criterion is unique within a tender
    _sql_constraints = [
        ('unique_criterion_per_tender', 'UNIQUE(criterion_id, tender_id)', 'Each criterion must be unique per tender.'),
    ]

    @api.constrains('actual_score', 'assigned_target')
    def _check_actual_score(self):
        for record in self:
            if record.actual_score > record.assigned_target:
                raise ValidationError("The actual score cannot be greater than the assigned target.")

    @api.model
    def create_scores_for_criteria(self, tender_id):
        # Get all criteria records
        criteria_records = self.env['tender.evaluation.criteria'].search([])

        # Create a score record for each criterion
        for criterion in criteria_records:
            self.create({
                'criterion_id': criterion.id,
                'assigned_target': 0.0,  # Default value, can be modified later
                'tender_id': tender_id,
            })