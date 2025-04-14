from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    allowed_warehouses_ids = fields.Many2many(
        'stock.warehouse',
        string='Allowed Warehouses',
        help='Warehouses that the user is allowed to access.',
        store=True
    )
    
    
    @api.model
    def create(self, vals):
        self.clear_caches()
        return super(ResUsers, self).create(vals)

    def write(self, vals):
        # if vals;['allowed_warehouses_ids']:
        #     print("in here")
        self.clear_caches()
            
        return super(ResUsers, self).write(vals)
    