from odoo import fields, models, api


class AddisSystemsStockPickingInherited(models.Model):
    _inherit = 'stock.picking'

    @api.onchange('location_id')
    def _onchange_source_location_id(self):
        if self.location_id:
            if self.location_dest_id and self.location_id == self.location_dest_id:
                self.location_dest_id = None

    @api.onchange('location_dest_id')
    def _onchange_destination_location(self):
        if self.location_dest_id:
            if self.location_id and self.location_id == self.location_dest_id:
                self.location_dest_id = None