# from odoo import models, fields, api

# class Component(models.Model):
#     _name = 'equipment.management.component'
#     _description = 'Equipment Component'

#     name = fields.Char('Component Name', required=True)
#     equipment_id = fields.Many2one('equipment.management.equipment', string='Equipment', required=True)
#     status = fields.Selection([
#         ('working', 'Working'),
#         ('not_working', 'Not Working'),
#         ('under_maintenance', 'Under Maintenance')
#     ], default='working')
#     is_working = fields.Boolean('Is Working', default=True)  # True if the component is working, False if not

#     def send_notification(self):
#         """Send email notification if the component is not working."""
#         template = self.env.ref('equipment_management.notification_template_component_failure')
#         self.env['mail.template'].browse(template.id).send_mail(self.id)


# # from odoo import models, fields

# # class MrpWorkcenter(models.Model):
# #     _inherit = 'mrp.workcenter'

# #     equipment_id = fields.Many2one(
# #         'equipment.management.equipment', string="Equipment",
# #         help="Select the equipment associated with this work center."
# #     )


from odoo import models, fields, api, _

class Component(models.Model):
    _name = 'equipment.management.component'
    _description = 'Equipment Component'

    name = fields.Char('Component Name', required=True)
    equipment_id = fields.Many2one('equipment.management.equipment', string='Equipment', required=True)
    status = fields.Selection([
        ('working', 'Working'),
        ('not_working', 'Not Working'),
        ('under_maintenance', 'Under Maintenance')
    ], default='working')
    is_working = fields.Boolean('Is Working', compute='_compute_is_working', store=True)

    @api.depends('status')
    def _compute_is_working(self):
        """Automatically set is_working based on the status."""
        for record in self:
            record.is_working = record.status == 'working'

    def send_notification(self):
        """Send email notification if the component is not working."""
        for record in self:
            if record.status == 'not_working':
                template = self.env.ref('equipment_management.notification_template_component_failure')
                self.env['mail.template'].browse(template.id).send_mail(record.id)