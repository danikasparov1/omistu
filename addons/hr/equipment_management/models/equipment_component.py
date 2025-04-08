from odoo import models, fields

class EquipmentComponent(models.Model):
    _name = 'equipment.management.equipment_component'
    _description = 'Equipment Component Link'

    equipment_id = fields.Many2one('equipment.management.equipment', string='Equipment', required=True)
    component_id = fields.Many2one('equipment.management.component', string='Component', required=True)
