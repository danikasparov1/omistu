from odoo import fields, api, models
import logging

from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)

class MrpProduction(models.Model):
    _inherit = "mrp.production"

    mrp_plan = fields.Many2one("mrp.planing", string="Manufacturing Plan")



    
class StorePicking(models.Model):
    _inherit = "stock.picking"

    is_customers = fields.Boolean(string="Quality Check")

    def create_mo(self):
        for rec in self:
            if rec.is_customers:
                _logger.info(f"*** Quality Check enabled: {rec.is_customers}")
                
                # Check if a manufacturing order already exists for this picking
                existing_mo = self.env['mrp.production'].search([('grn_id', '=', rec.id)])
                _logger.info(f"*** Existing MOs count: {len(existing_mo)}")
                
                if not existing_mo:
                    for move_line in rec.move_ids:
                        _logger.info(f"*** Creating MO for product {move_line.product_id.id} in GRN {rec.name}")

                        # Create the MO and log the result
                        mo = self.env['mrp.production'].create({
                            'product_id': move_line.product_id.id,
                            'product_qty': 1,
                            'is_customers': True,
                        })

                        # Set the grn_id to the current picking's ID
                        mo.grn_id = rec.id
                        _logger.info(f"*** MO created with ID {mo.id} and linked to GRN {rec.name}")
                else:
                    raise UserError("Manufacturing Order already exists.")