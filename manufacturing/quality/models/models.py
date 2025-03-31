from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class CheckFields(models.Model):
    _name = "quality.check.field"
    _description = "Quality assurance check field"

    name = fields.Char(string="Check Field", required=True)


class UnitOfMeasure(models.Model):
    _name = 'quality.metric.unit'
    _description = "A unit of measurement for a numeric measure of a quality."

    name = fields.Char(string="Unit Name")


class CheckState(models.Model):
    _name = "quality.check.state"
    _description = "Check State for Check Fields"

    check_field_id = fields.Many2one(
        'quality.check.field',  
        string="Check Field",
        help="The check field this state belongs to"
    )
    stage_field_id = fields.Many2one(
            'quality.stage.fields',  
            string="Stage Field",
            required=True,
            default=lambda self: self.env['quality.stage.fields'].search([], limit=1).id
        )

    start_threshold = fields.Float(
        string="Min. Value", 
        help="Minimum value required for the test to pass"
    )
    end_threshold = fields.Float(
        string="Max. Value", 
        help="Maximum value required for the test to pass"
    )
    test_quantity = fields.Integer(
        string="Test Quantity", 
        default=-1,
        help="Quantity of items tested"
    )
    is_checked = fields.Boolean(
        string="Checked",
        compute="_compute_is_checked",
        store=True,
        help="Indicates if the test passed the threshold"
    )
    unit = fields.Many2one(
        'quality.metric.unit', 
        string="Unit", 
        help="Measurement unit for the test"
    )
    numeric_measure = fields.Boolean(
        string="Numeric Measure", 
        default=False,
        help="Indicates if the test is a numeric measure"
    )
    test_id = fields.Many2one(
        'quality.product.test',
        string="Test",
        ondelete="cascade",
        help="The product test this check state is linked to"
    )

    @api.depends('test_quantity', 'start_threshold', 'end_threshold', 'numeric_measure')
    def _compute_is_checked(self):
        for record in self:
            if record.start_threshold and record.end_threshold:
                record.is_checked = record.start_threshold <= record.test_quantity <= record.end_threshold
            else:
                record.is_checked = False


class StageFields(models.Model):
    _name = "quality.stage.fields"
    _description = "Quality assurance check fields for each manufacturing stage"
    
    name = fields.Char(string="Name", compute="_get_name", store=True)
    stage_id = fields.Many2one(
        'mrp.stage.name', 
        string="Stage", 
        required=True
    )
    check_field_ids = fields.Many2many(
        'quality.check.field', 
        string="Check Fields"
    )
    check_states = fields.One2many(
        'quality.check.state', 
        'stage_field_id', 
        string="Check States"
    )

    @api.depends('stage_id')
    def _get_name(self):
        for record in self:
            record.name = record.stage_id.name if record.stage_id else "No Stage"
