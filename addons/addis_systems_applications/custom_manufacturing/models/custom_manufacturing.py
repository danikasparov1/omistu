# custom_manufacturing/models/custom_manufacturing.py
from odoo import models, fields

class CustomManufacturing(models.Model):
    _name = 'custom.manufacturing'
    _description = 'Custom Manufacturing'

    name = fields.Char(string='Name', required=True)
    custom_field = fields.Char(string='Measure')
    # Add more fields as neededMeasure



# custom_manufacturing/models/custom_manufacturing_extension.py
from odoo import models, fields, api

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    custom_field = fields.Char(string='Measure')

    @api.model
    def add_custom_fields(self):
        custom_fields = self.env['custom.manufacturing'].fields_get()
        for field_name, field_info in custom_fields.items():
            if field_name not in ['id', 'create_uid', 'create_date', 'write_uid', 'write_date', '__last_update']:
                field_type = field_info['type']
                field_label = field_info['string']
                self.env['ir.model.fields'].create({
                    'name': field_name,
                    'model_id': self.env['ir.model']._get('mrp.production').id,
                    'field_description': field_label,
                    'ttype': field_type,
                })

    @api.model
    def create(self, vals):
        res = super(MrpProduction, self).create(vals)
        self.add_custom_fields()
        return res

    def write(self, vals):
        res = super(MrpProduction, self).write(vals)
        self.add_custom_fields()
        return res