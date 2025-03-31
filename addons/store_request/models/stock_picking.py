from odoo import models, fields

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    supplier_invoice_no = fields.Char(string="Supplier's Invoice No")
    lc_no = fields.Char(string="Letter of Credit No")
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')
    location_id = fields.Many2one('stock.location', string='Location', related='warehouse_id.view_location_id')
    store_code = fields.Char(string="Store Code")
    classification = fields.Selection([
        ('raw_material', 'Raw Material'),
    ], string="Classification")
    purchase_requisition_no = fields.Many2one('purchase.request', string="Purchase Requisition No")
    purchase_order_no = fields.Many2one('purchase.order', string="Purchase Order No")
    delivery_type = fields.Selection([
        ('complete', 'Complete'),
        ('partial', 'Partial'),
    ], string="Delivery")
    truck_plate_no = fields.Char(string="Truck Plate No")
    item_type = fields.Selection([
        ('spare', 'Spare Parts'),
        ('consumable', 'Consumable'),
    ], string="Item Type")

    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        for picking in self:
            for line in picking.move_ids_without_package:
                if picking.picking_type_id.code == 'outgoing':  # Only for outgoing deliveries
                    equipment_issues = self.env['equipment.issue'].search([
                        ('state', '=', 'draft'),
                        ('product_id', '=', line.product_id.id)
                    ])
                    for issue in equipment_issues:
                        issue.state = 'issue'  # Update state to 'issued' (or your relevant state)

                if picking.picking_type_id.code == 'incoming':  # For stock returns
                    equipment_issues = self.env['equipment.issue'].search([
                        ('state', '=', 'pending'),
                        ('product_id', '=', line.product_id.id)
                    ])
                    for issue in equipment_issues:
                        issue.state = 'returned'  # Update the state to 'returned'

        return res
