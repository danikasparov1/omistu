from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    check_id = fields.Many2one('quality.check', string='Quality Inspection')
    check_ids = fields.One2many('quality.check', 'stock_id', 'Checks')
    check_count = fields.Integer(string="Checks", compute='_compute_show_check_count')
    quality_state = fields.Selection(string='Quality Check', related='check_id.quality_state', readonly=True, store=True)
    
    # check_count = 
    
    
    @api.depends('check_ids')
    def _compute_show_check_count(self):
        self.check_count = len(self.check_ids)
    
    @api.model
    def create(self, vals):
        picking = super(StockPicking, self).create(vals)
        
        
        

        if picking.picking_type_id.code == 'incoming': # Assuming 'incoming' is the code for purchase orders
            check = self.env['quality.check'].create({
                'stock_id': picking.id,
                'origin': picking.origin
            })
            
            picking.write({'check_id': check.id})
            
            
 
        # check = self.env['quality.check'].create({
        #     'stock_id': picking.id,
        #     'origin': picking.origin
        # })
        
        # picking.write({'check_id': check.id})
        
        return picking
    
    
    
    def action_check_count(self):
        return len(self.check_ids)
    
    
    
    

    def button_validate(self):
        
           
            if self.check_id and self.quality_state == 'draft':
                print("in draft")
                raise ValidationError("እባክዎ ከመቀጠልዎ በፊት የምርቶቹን ጥራት ያረጋግጡ።")

            
            # if self.check_id and self.quality_state == 'failed':
            #     purchase_order = self.env['purchase.order'].search([('stock_picking_ids', 'in', self.ids)], limit=1)
            #     if purchase_order:
            #         purchase_order.action_cancel()
            #     self.action_cancel()
                
                return True

                
                
            
            if (self.check_id and self.quality_state=='passed') or not self.check_id:
                # Clean-up the context key at validation to avoid forcing the creation of immediate
                # transfers.
                ctx = dict(self.env.context)
                ctx.pop('default_immediate_transfer', None)
                self = self.with_context(ctx)

                # Sanity checks.
                if not self.env.context.get('skip_sanity_check', False):
                    self._sanity_check()

                self.message_subscribe([self.env.user.partner_id.id])

                # Run the pre-validation wizards. Processing a pre-validation wizard should work on the
                # moves and/or the context and never call `_action_done`.
                if not self.env.context.get('button_validate_picking_ids'):
                    self = self.with_context(button_validate_picking_ids=self.ids)
                res = self._pre_action_done_hook()
                if res is not True:
                    return res

                # Call `_action_done`.
                pickings_not_to_backorder = self.filtered(lambda p: p.picking_type_id.create_backorder == 'never')
                if self.env.context.get('picking_ids_not_to_backorder'):
                    pickings_not_to_backorder |= self.browse(self.env.context['picking_ids_not_to_backorder']).filtered(
                        lambda p: p.picking_type_id.create_backorder != 'always'
                    )
                pickings_to_backorder = self - pickings_not_to_backorder
                pickings_not_to_backorder.with_context(cancel_backorder=True)._action_done()
                pickings_to_backorder.with_context(cancel_backorder=False)._action_done()

                if self.user_has_groups('stock.group_reception_report'):
                    pickings_show_report = self.filtered(lambda p: p.picking_type_id.auto_show_reception_report)
                    lines = pickings_show_report.move_ids.filtered(lambda m: m.product_id.type == 'product' and m.state != 'cancel' and m.quantity_done and not m.move_dest_ids)
                    if lines:
                        # don't show reception report if all already assigned/nothing to assign
                        wh_location_ids = self.env['stock.location']._search([('id', 'child_of', pickings_show_report.picking_type_id.warehouse_id.view_location_id.ids), ('usage', '!=', 'supplier')])
                        if self.env['stock.move'].search([
                                ('state', 'in', ['confirmed', 'partially_available', 'waiting', 'assigned']),
                                ('product_qty', '>', 0),
                                ('location_id', 'in', wh_location_ids),
                                ('move_orig_ids', '=', False),
                                ('picking_id', 'not in', pickings_show_report.ids),
                                ('product_id', 'in', lines.product_id.ids)], limit=1):
                            action = pickings_show_report.action_view_reception_report()
                            action['context'] = {'default_picking_ids': pickings_show_report.ids}
                            return action
                
                
                
                
                return True


        
    
    # quality_check_todo = fields.Boolean('Pending checks', compute='_compute_check')
    # quality_check_fail = fields.Boolean(compute='_compute_check')
    # def _compute_check(self):
    #     for picking in self:
    #         todo = False
    #         fail = False
    #         checkable_products = picking.mapped('move_line_ids').mapped('product_id')
            
    #         for check in picking.check_ids:
    #             if check.quality_state == 'none' and (check.product_id in checkable_products or check.measure_on == 'operation'):
    #                 todo = True
    #             elif check.quality_state == 'fail':
    #                 fail = True
    #             if fail and todo:
    #                 break
    #         picking.quality_check_fail = fail
    #         picking.quality_check_todo = todo


    # @api.depends('quality_check_todo')
    # def _compute_show_validate(self):
    #     super()._compute_show_validate()
    #     for picking in self:
    #         if picking.quality_check_todo:
                # picking.show_validate = False

    # def check_quality(self):
    #     self.ensure_one()
    #     checkable_products = self.mapped('move_line_ids').mapped('product_id')
    #     checks = self.check_ids.filtered(lambda check: check.quality_state == 'none' and (check.product_id in checkable_products or check.measure_on == 'operation'))
    #     if checks:
    #         return checks.action_open_quality_check_wizard()
    #     return False

    # def _create_backorder(self):
    #     res = super(StockPicking, self)._create_backorder()
    #     if self.env.context.get('skip_check'):
    #         return res
    #     for backorder in res:
    #         backorder.backorder_id.check_ids.filtered(lambda qc: qc.quality_state == 'none').sudo().unlink()
    #         backorder.move_ids._create_quality_checks()
    #     return res

    # def _action_done(self):
    #     # Do the check before transferring
    #     product_to_check = self.mapped('move_line_ids').filtered(lambda x: x.qty_done != 0).mapped('product_id')
    #     if self.mapped('check_ids').filtered(lambda x: x.quality_state == 'none' and x.product_id in product_to_check):
    #         raise UserError(_('You still need to do the quality checks!'))
    #     return super(StockPicking, self)._action_done()

    # def _pre_action_done_hook(self):
    #     res = super()._pre_action_done_hook()
    #     if res is True:
    #         pickings_to_check_quality = self._check_for_quality_checks()
    #         if pickings_to_check_quality:
    #             return pickings_to_check_quality[0].with_context(pickings_to_check_quality=pickings_to_check_quality.ids).check_quality()
    #     return res

    # def _check_for_quality_checks(self):
    #     quality_pickings = self.env['stock.picking']
    #     for picking in self:
    #         product_to_check = picking.mapped('move_line_ids').filtered(lambda ml: ml.qty_done != 0).mapped('product_id')
    #         if picking.mapped('check_ids').filtered(lambda qc: qc.quality_state == 'none' and qc.product_id in product_to_check):
    #             quality_pickings |= picking
    #     return quality_pickings

    # def action_cancel(self):
    #     res = super(StockPicking, self).action_cancel()
    #     self.sudo().mapped('check_ids').filtered(lambda x: x.quality_state == 'none').unlink()
    #     return res

    # def action_open_quality_check_picking(self):
    #     action = self.env["ir.actions.actions"]._for_xml_id("quality_control.quality_check_action_picking")
    #     action['context'] = self.env.context.copy()
    #     action['context'].update({
    #         'search_default_picking_id': [self.id],
    #         'default_picking_id': self.id,
    #         'show_lots_text': self.show_lots_text,
    #     })
    #     return action



