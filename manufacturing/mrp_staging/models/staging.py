from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class ProductionSteps(models.Model):
    _name = 'mrp.production.steps'
    _description = 'Production Steps'

    name = fields.Char(string="Step Name", required=True)
    step_no = fields.Integer(string="Step Number", required=True, help="Order of the step within the stage.")
    stage_id = fields.Many2one('mrp.stage.name', string="Stage", required=True, ondelete='cascade')


class StageName(models.Model):
    _name = 'mrp.stage.name'
    _description = 'Production Stages'

    name = fields.Char(string="Stage Name", required=True)
    sequence = fields.Integer(string="Sequence", default=0)
    steps = fields.One2many('mrp.production.steps', 'stage_id', string="Steps")
    ordered_steps = fields.One2many('mrp.production.steps', 'stage_id', string="Ordered Steps", compute="_compute_ordered_steps")

    @api.depends('steps')
    def _compute_ordered_steps(self):
        for record in self:
            record.ordered_steps = record.steps.sorted('step_no')



class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    production_type = fields.Selection(
        [('CKD', 'CKD'), ('SKD', 'SKD')],
        string="Production Type",
        default="CKD",
      
    )
    current_stage = fields.Many2one(
        'mrp.stage.name',
        string="Current Stage",
        compute="_compute_current_stage",
        store=True
    )
    current_step = fields.Many2one(
        'mrp.production.steps',
        string="Current Step",
        compute="_compute_current_step",
        store=True
    )
    on_qa = fields.Boolean(string="On QA", default=False,compute="_set_on_qa", store=True)

    @api.depends('current_step')
    def _compute_current_stage(self):
        for record in self:
            if record.current_step:
                record.current_stage = record.current_step.stage_id
            else:
                record.current_stage = False

    @api.depends('production_type', 'current_stage')
    def _compute_current_step(self):
        for record in self:
            
            if record.production_type and not record.current_stage:
                # Initialize with the first stage
                stage = self.env['mrp.stage.name'].search([], order='id', limit=1)
                if stage and stage.ordered_steps:
                    record.current_stage = stage
                    record.current_step = stage.ordered_steps[0]
                else:
                    record.current_step = False
            else:
                # Retain the current step if already set
                if record.current_stage.ordered_steps:
                    record.current_step = record.current_step or record.current_stage.ordered_steps[0]
                else:
                    record.current_step = False

    def proceed_to_next_step(self):
        for record in self:
            if record.current_step:
                _logger.info(f"*** {record.state}")
                next_step = self.env['mrp.production.steps'].search([
                    ('stage_id', '=', record.current_stage.id),
                    ('step_no', '>', record.current_step.step_no)
                ], order='step_no', limit=1)

                if next_step:
                    record.current_step = next_step
                else:
                    # self._set_on_qa()
                    pass
                    
            else:
                _logger.warning(f"No current step found for production order {record.name}.")

    @api.model
    def create(self, vals):
        record = super(MrpProduction, self).create(vals)
        if record.current_stage:
            qa_test = self.env['quality.assurance'].create({
                'production_id': record.id,
                'product_id': record.product_id.id,
                'stage_id': record.current_stage.id,
                'is_external': False
            })
            _logger.info(f"Quality test created for {record.name} at stage {record.current_stage.name} -- {qa_test.id}")
        return record

    def _set_on_qa(self):
        for record in self:
            next_step = self.env['mrp.production.steps'].search([
                        ('stage_id', '=', record.current_stage.id),
                        ('step_no', '>', record.current_step.step_no)
            ], order='step_no', limit=1)

            if next_step:
                record.current_step = next_step
            else:
                record.on_qa=True
    def mark_all_steps_done(self):
        for record in self:
            if record.current_stage:
                steps = record.current_stage.ordered_steps
                steps.write({'status': 'done'})
                record.proceed_to_next_step()
            else:
                _logger.warning(f"No current stage found for production order {record.name}.")

    def on_test_pass(self):
        pass
        for record in self:
            if record.on_qa:
                _logger.info(f"** Test passed for {record.name} **")
                record.write({'on_qa': False})
                _logger.info(f"*****  {record.current_stage.sequence}")
                next_stage = self.env['mrp.stage.name'].search([
                    ('sequence', '>', record.current_stage.sequence)
                ], limit=1)
                _logger.info(f"******* {next_stage}")
                if next_stage:
                    record.current_stage = next_stage
                    record.current_step = next_stage.ordered_steps[0] if next_stage.ordered_steps else False
                    
                    _logger.info(f"Quality test created for {record.name} at stage {record.current_stage.name} -- {qa_test.id}")
                    return
                else:
                    _logger.info(f"** No next stage, incrementing qty_producing **")
                    record.qty_producing += 1 

                    initial_stage = self.env['mrp.stage.name'].search([
                        ('sequence', '>=',0)
                
                        ],  limit=1)
                    _logger.info(f"***** {initial_stage}")
                    if initial_stage:
                        record.current_stage = initial_stage
                        record.current_step = initial_stage.ordered_steps[0] if initial_stage.ordered_steps else False

    def on_test_fail(self):
        for record in self:
            _logger.info(f"** Test failed for {record.name} **")
            record.write({'on_qa': False})

            current_stage_fetch = self.env['mrp.stage.name'].search([
                ('id', '=', record.current_stage.id)
            ], order='id', limit=1)

            if current_stage_fetch:
                record.current_stage = current_stage_fetch
                record.current_step = current_stage_fetch.ordered_steps[0] if current_stage_fetch.ordered_steps else False
            else:
                _logger.warning(f"Stage fetch failed for {record.name}.")

