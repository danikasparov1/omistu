from odoo import models, fields, api
from odoo.exceptions import UserError,ValidationError

import logging

_logger = logging.getLogger(__name__)
class QualityCheckTemplate(models.Model):
    _name = 'quality.check.template'
    _description = 'Quality Check Template'

    name = fields.Char(string="Check Field", required=True)
    stage_id = fields.Many2one('mrp.workcenter', string="Stage", required=True)  
    min_threshold = fields.Float(string="Min Threshold", required=True)
    max_threshold = fields.Float(string="Max Threshold", required=True)
    description = fields.Text(string="Description")

class QualityAssurance(models.Model):
    _name = 'quality.assurance'
    _order = 'id desc'
    _description = 'Quality Assurance'

    product_id = fields.Many2one('product.product', string="Product", required=True) 
    stage_id = fields.Many2one('mrp.workcenter', string="Stage", required=True)  
    test_instance_ids = fields.One2many('quality.test.instance', 'quality_assurance_id', string="Quality Tests")
    pass_field = fields.Boolean(string="Pass/Fail", compute="_compute_pass_field", store=True)
    production_id= fields.Many2one('mrp.production')
    is_external = fields.Boolean(string="External Test", default=False)
    client_id = fields.Many2one('res.partner', string="Client")  
    none_stock= fields.Many2one('stock.none.stock')
    maintenance_request_ids = fields.One2many('maintenance.request', 'quality_assurance_id', string="Maintenance Requests")
    not_tested= fields.Boolean(default=True)
    description = fields.Text(string="Description")
    @api.onchange('product_id', 'stage_id')
    def _onchange_product_stage(self):
        """Fetch quality checks for the product and stage."""
        if self.product_id and self.stage_id:
            # Clear existing test instances
            self.test_instance_ids = [(5, 0, 0)]

            # Fetch quality check templates for the stage
            templates = self.env['quality.check.template'].search([
                ('stage_id', '=', self.stage_id.id),
                # ('is_external', '=', self.is_external or False)
            ])


            if templates:
                # Create test instances based on templates
                test_instances = []
                for template in templates:
                    _logger.info(f"*****{template.id}")
                    test_instances.append((0, 0, {
                        'check_field': template.id,  # Ensure check_field is properly set
                        'min_threshold': template.min_threshold,
                        'max_threshold': template.max_threshold,
                    }))
                
                self.test_instance_ids = test_instances
            else:
                # Handle the case where no templates are found
                raise UserError("No quality check templates found for the selected stage.")
        else:
            # Clear test instances if no product or stage is selected
            self.test_instance_ids = [(5, 0, 0)]


    @api.model
    def create(self, values):
        # Assuming `stage_id` is part of `values`
        stage_id = values.get('stage_id')
        templates = self.env['quality.check.template'].search([('stage_id', '=', stage_id)])
        
        # Create the record first
        record = super(QualityAssurance, self).create(values)

        # Delete existing related test instances
        self.env['quality.test.instance'].search([('quality_assurance_id', '=', record.id)]).unlink()

        # Create new related test instances
        test_instances = []
        for template in templates:
            _logger.info(f"**(((**(( {template.id})))))")
            test_instance = self.env['quality.test.instance'].create({
                'check_field': template.id, 
                'min_threshold': template.min_threshold,
                'max_threshold': template.max_threshold,
                'quality_assurance_id': record.id
            })
            test_instances.append((4, test_instance.id))  # Append the correct reference

        # Assign the test instances to the record
        record.write({'test_instance_ids': test_instances})

        return record
    @api.depends('test_instance_ids.test_value')
    def _check_tested(self):
        for r in self:
            r.not_tested = all(test.test_value==0.0 for test in r.test_instance_ids)
    
    @api.depends('test_instance_ids.pass_field')
    def _compute_pass_field(self):
        """Compute overall pass/fail based on test instances."""
        for record in self:
            # If all test instances have pass_field set to True, then Pass
            record.pass_field = all(test.pass_field for test in record.test_instance_ids)
            if record.pass_field:
                self._set_tested()
                self.mark_passed()

            
    def _set_tested(self):
        for record in self:
            record.not_tested = False
    def mark_failed(self):
        for record in self:
            if not record.description:
                raise ValidationError(f"Please provide a description for the failed quality assurance test.")       
            maintenance_request = self.env['maintenance.request'].create({
                'name': f"Corrective Maintenance for {record.product_id.name}",
                'description': f"Quality assurance failed at stage: {record.stage_id.name}. Please investigate and resolve.\n {record.description}",
                'stage_id': record.stage_id.id,
                'production_id': record.production_id.id,
                'quality_assurance_id': record.id,
            })
            self._set_tested()
            _logger.info(f"Created maintenance request: {maintenance_request.name} - {self.not_tested}")

    
    def mark_passed(self):
        for record in self:
            if not record.is_external:
                
                record.production_id.on_test_pass() 
            else:
                record.none_stock.on_qa = False 
                record.none_stock.status= "certified"
                
class QualityTestInstance(models.Model):
    _name = 'quality.test.instance'
    _description = 'Quality Test Instance'

    quality_assurance_id = fields.Many2one('quality.assurance', string="Quality Assurance")
    check_field = fields.Many2one('quality.check.template', string="Check Field")
    min_threshold = fields.Float(string="Min Threshold")
    max_threshold = fields.Float(string="Max Threshold")
    test_value = fields.Float(string="Test Value", default=0.0)
    pass_field = fields.Boolean(string="Pass", compute="_compute_pass_field", store=True)

    @api.depends('test_value', 'min_threshold', 'max_threshold')
    def _compute_pass_field(self):
        for record in self:
            # Determine if the test value is within the threshold range
            record.pass_field = record.min_threshold <= record.test_value <= record.max_threshold
    


class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'
    _order="id desc"
    quality_assurance_id = fields.Many2one('quality.assurance', string="Quality Assurance")
    production_id = fields.Many2one('mrp.production', string="Manufacturing Order")
    done_Field = fields.Boolean(default=False, compute="_action_done", store=True)
    
    # TODO: if this maintenance is complete and it is a corrective maintenance, create a new qa for the same product of the production_id, stage and production
    @api.depends('stage_id')
    def _action_done(self):
        for record in self:
            _logger.info(f"**{record.stage_id.name}")   
            if record.stage_id.name == 'Repaired':
                if record.production_id:
             

                    # Reset the previous quality assurance object
                    record.quality_assurance_id.write({
                        'not_tested': True,
                        'pass_field': False,
                    })

                    # Reset test values of the test instances
                    for test_instance in record.quality_assurance_id.test_instance_ids:
                        test_instance.write({
                            'test_value': 0.0,
                            'pass_field': False,
                        })

                    _logger.info(f"Reset QA: {record.quality_assurance_id.id} and its test instances")
