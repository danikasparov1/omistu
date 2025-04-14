from odoo import models, fields

class ManufacturingOtherFields(models.Model):
    _name = 'manufacturing.other.fields'
    _description = 'Manufacturing Other Fields'

    name = fields.Char(string="Name", required=True)
    other_field_1 = fields.Char(string="Description")
    other_field_2 = fields.Integer(string="Amount")
    other_field_3 = fields.Boolean(string="By our employee only")
from odoo import models, fields

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    manufacturing_other_fields_ids = fields.Many2many(
        comodel_name='manufacturing.other.fields',
        string="provided service",
        help="Additional fields related to manufacturing."
    )


from odoo import models, fields, api
from odoo.exceptions import ValidationError

class MrpWorkOrder(models.Model):
    _inherit = 'mrp.workorder'

    labor_charge = fields.Float(
        string="Labor Charge",
        required=True,
        help="Cost of labor for this work order",
    )
    mechanic_number = fields.Char(
        string="Mechanic Number",
        required=True,
        help="ID of the mechanic assigned to this work order",
    )

    @api.constrains('labor_charge', 'mechanic_number')
    def _check_fields(self):
        for record in self:
            if record.labor_charge <= 0:
                raise ValidationError("Labor Charge must be greater than zero.")
            if not record.mechanic_number or not record.mechanic_number.strip():
                raise ValidationError("Mechanic Number cannot be blank.")

class ManufacturingOtherFieldsnew(models.Model):
    _name = 'manufacturing.other.fields.new'
    _description = 'Manufacturing Other Fields New'

    name = fields.Char(string="Name", required=True)
    other_field_1 = fields.Char(string="Description")
    other_field_2 = fields.Integer(string="Amount")
    other_field_3 = fields.Boolean(string="By our employee only")


from odoo import models, fields

class CustomFieldsModel(models.Model):
    _name = 'custom.fields.model'
    _description = 'Custom Fields Model'

    name = fields.Char(string='Field Name', required=True)
    field_type = fields.Selection([
        ('char', 'Char'),
        ('integer', 'Integer'),
        ('float', 'Float'),
        ('boolean', 'Boolean'),
        ('text', 'Text'),
        ('many2one', 'Many2one'),
        ('one2many', 'One2many'),
        ('many2many', 'Many2many')
    ], string='Field Type', required=True)



from odoo import models, fields, api
from odoo.exceptions import ValidationError

class MrpWorkOrder(models.Model):
    _inherit = 'mrp.workorder'

    labor_charge = fields.Float(
        string="Labor Charge",
        required=True,
        help="Cost of labor for this work order",
    )
    mechanic_number = fields.Char(
        string="Mechanic Number",
        required=True,
        help="ID of the mechanic assigned to this work order",
    )

    @api.constrains('labor_charge', 'mechanic_number')
    def _check_fields(self):
        for record in self:
            if record.labor_charge <= 0:
                raise ValidationError("Labor Charge must be greater than zero.")
            if not record.mechanic_number or not record.mechanic_number.strip():
                raise ValidationError("Mechanic Number cannot be blank.")

    @api.model
    def add_custom_fields(self):
        custom_fields = self.env['custom.fields.model'].search([])
        for field in custom_fields:
            field_name = field.name
            field_type = field.field_type
            if field_type == 'char':
                self._add_field(field_name, fields.Char(string=field_name))
            elif field_type == 'integer':
                self._add_field(field_name, fields.Integer(string=field_name))
            elif field_type == 'float':
                self._add_field(field_name, fields.Float(string=field_name))
            elif field_type == 'boolean':
                self._add_field(field_name, fields.Boolean(string=field_name))
            elif field_type == 'text':
                self._add_field(field_name, fields.Text(string=field_name))
            elif field_type == 'many2one':
                self._add_field(field_name, fields.Many2one('res.partner', string=field_name))
            elif field_type == 'one2many':
                self._add_field(field_name, fields.One2many('res.partner', 'workorder_id', string=field_name))
            elif field_type == 'many2many':
                self._add_field(field_name, fields.Many2many('res.partner', string=field_name))