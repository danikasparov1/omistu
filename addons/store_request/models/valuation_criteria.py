from odoo import models, fields, api
from odoo.exceptions import ValidationError

class TenderEvaluationCriteria(models.Model):
    _name = 'tender.evaluation.criteria'
    _description = 'Tender Evaluation Criteria'

    name = fields.Char(string='Criterion', required=True)
    weight = fields.Float(string='Weight', required=True)

    @api.constrains('weight')
    def _check_total_weight(self):
        """
        Constraint to ensure the sum of all weights does not exceed 50.
        """
        total_weight = sum(self.search([]).mapped('weight'))
        if total_weight > 50:
            raise ValidationError("The total weight of all criteria cannot exceed 50.")

    @api.model
    def create(self, vals):
        """
        Override the create method to enforce the total weight constraint.
        """
        # Calculate the total weight of existing records
        total_weight = sum(self.search([]).mapped('weight'))
        # Add the weight of the new record being created
        new_weight = vals.get('weight', 0)
        if total_weight + new_weight > 50:
            raise ValidationError("The total weight of all criteria cannot exceed 50.")
        return super(TenderEvaluationCriteria, self).create(vals)