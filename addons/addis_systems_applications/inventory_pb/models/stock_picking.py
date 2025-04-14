from odoo import models, fields, api



class StockPicking(models.Model):
    _inherit = 'stock.picking'

    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Warehouse',
        compute='_compute_warehouse_id',
        store=True,
        readonly=True,
    )
    
    origin = fields.Char(
        'Source Document', index='trigram',
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Reference of the document")
    
    

    @api.depends('picking_type_id')
    def _compute_warehouse_id(self):
        for picking in self:
            picking.warehouse_id = picking.picking_type_id.warehouse_id
            
    
    @api.depends('state', 'move_ids')
    def _compute_show_mark_as_todo(self):
        for picking in self:
            picking.show_mark_as_todo = False
    
   

    @api.depends('state')
    def _compute_show_validate(self):
        for picking in self:
            if not (picking.immediate_transfer) and picking.state == 'draft':
                picking.show_validate = True
            elif picking.state not in ('draft', 'waiting', 'confirmed', 'assigned'):
                picking.show_validate = False
            else:
                picking.show_validate = True