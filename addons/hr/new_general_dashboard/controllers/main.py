from odoo import http
from odoo.http import request

class MyController(http.Controller):
    @http.route('/my_module/is_crm_installed', type='json', auth='user')
    def is_crm_installed(self):
        crm_installed = bool(request.env['ir.module.module'].search([('name', '=', 'crm'), ('state', '=', 'installed')], limit=1))
        return {'crm_installed': crm_installed}
