# from odoo import models, fields

# class ResConfigSettings(models.TransientModel):
#     _inherit = 'res.config.settings'

#     external_test_report_enabled = fields.Boolean(
#         string="Enable External Test Reports", 
#         default=False
#     )

#     def set_values(self):
#         super(ResConfigSettings, self).set_values()
#         self.env['ir.config_parameter'].sudo().set_param(
#             'quality.external_test_report_enabled', 
#             self.external_test_report_enabled
#         )
#         self._update_external_test_report_group(self.external_test_report_enabled)
        
#     def get_values(self):
#         # pass
#         res = super(ResConfigSettings, self).get_values()
#         IrConfig = self.env['ir.config_parameter'].sudo()
#         res.update(
#             external_test_report_enabled=IrConfig.get_param(
#                 'quality.external_test_report_enabled', 
#                 default=False
#             )
#         )
#         return res

#     # def _update_external_test_report_group(self, enabled):
#     #     group = self.env.ref('your_module.group_external_test_report_enabled')
#     #     users = self.env['res.users'].search([])
#     #     if enabled:
#     #         users.write({'groups_id': [(4, group.id)]})  # Add group
#     #     else:
#     #         users.write({'groups_id': [(3, group.id)]})  # Remove group
