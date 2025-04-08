from odoo import models, fields, api

class Equipment(models.Model):
    _name = 'equipment.management.equipment'
    _description = 'Equipment Management'

    name = fields.Char('Equipment Name', required=True)
    description = fields.Text('Description')
    components = fields.One2many('equipment.management.component', 'equipment_id', string='Components')
    status = fields.Selection([
        ('working', 'Working'),
        ('not_working', 'Not Working'),
        ('under_maintenance', 'Under Maintenance')
    ], default='working')

    workcenter_id = fields.Many2one(
        'mrp.workcenter', string="Work Center",
        help="The work center this equipment is associated with."
    )

    @api.model
    def create(self, vals):
        equipment = super(Equipment, self).create(vals)
        equipment.check_components()
        return equipment

    def check_components(self):
        """Checks components for malfunctions and sends an email if not working."""
        for component in self.components:
            if not component.is_working:
                component.send_notification()


from odoo import models, fields

class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    equipment_ids = fields.One2many(
        'equipment.management.equipment', 'workcenter_id', string="Equipment",
        help="List of equipment associated with this work center."
    )

from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_finished_product = fields.Boolean(
        string="Is Finished Product",
        help="Indicates whether this product is a finished product (manufactured)."
    )