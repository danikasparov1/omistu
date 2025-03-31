from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

class ExternalTestReport(models.Model):
    _name = "quality.external.test"
    _description = 'External quality test report model with pdf'

    qa = fields.Many2one('quality.assurance', domain=[('is_external', '=', True)], string="Test Id")
    name = fields.Char(compute="_get_product_name", store=True, default="New")
    customer = fields.Char(string="Customer", compute="_compute_customer", store=True)
    related_tests = fields.One2many(
        'quality.assurance',
        compute='_compute_related_tests',
        string="Related Quality Tests",
        readonly=True
    )

    @api.depends('qa')
    def _get_product_name(self):
        for rec in self:
            if rec.qa:
                rec.name = f"Test ON {rec.qa.product_id.name}"

   

    @api.depends('qa')
    def _compute_customer(self):
        
        for rec in self:
            if rec.qa:
                rec.customer = rec.qa.none_stock.customer.name

    @api.depends('qa')
    def _compute_related_tests(self):
       
        for record in self:
            if record.qa and record.qa.none_stock:
                record.related_tests = self.env['quality.assurance'].search([
                    ('none_stock', '=', record.qa.none_stock.id)
                ])
                _logger.info(f"**** {len(record.related_tests)}")
            else:
                record.related_tests = False
