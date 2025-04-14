from odoo import models, fields, api
# from odoo.exceptions import ValidationError    
class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    
    check_id = fields.Many2one('quality.check', string='Quality Inspection')
    quality_state = fields.Selection(string='Quality Check', related='check_id.quality_state', readonly=True, store=True)
    
    
    # def button_confirm(self):
        
        
        # for order in self:
        #     if order.state not in ['draft', 'sent']:
        #         continue
        #     order.order_line._validate_analytic_distribution()
        #     order._add_supplier_to_product()
        #     # Deal with double validation process
        #     if order._approval_allowed():
        #         order.button_approve()
                
        #         self.flush()

        #         if not order.check_id:
        #             print("Creating quality check for order:", order.name)
        #             stock_picking_records = self.env['stock.picking'].search([
        #                 ('state', '=', 'draft'),
        #                 ('origin', '=', self.name),
        #             ])
        #             print("Found stock picking records:", stock_picking_records)
        #             for stock_picking_rec in stock_picking_records:
        #                 check_id = self.env['quality.check'].create({
        #                     'stock_id': stock_picking_rec.id,
        #                 })
        #                 print("Created quality check:", check_id.id)
                    
                
                
                
                
                
        #     else:
        #         order.write({'state': 'to approve'})
        #     if order.partner_id not in order.message_partner_ids:
        #         order.message_subscribe([order.partner_id.id])
                

                
                

        # return True