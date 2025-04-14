from odoo import models, api, fields
from datetime import datetime

class ManufacturingCustomReportWizard(models.TransientModel):
    _name = 'mrp.production.wizard.report'
    _description = 'Custom Manufacturing Wizard Report'
    name = fields.Char(string="Report Name")  # Add this if missing
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    manufacturing_order_id = fields.Many2one('mrp.production', string="Manufacturing Order")
    product_id = fields.Many2one('product.product', string="Product")
    workcenter_id = fields.Many2one('mrp.workcenter', string="Workcenter")

    def manufacturing_by_order(self):
        domain = []

        if self.date_from:
            domain.append(('date_planned_start', '>=', self.date_from))
        
        if self.date_to:
            domain.append(('date_planned_start', '<=', self.date_to))
            
        if self.manufacturing_order_id:
            domain.append(('id', '=', self.manufacturing_order_id.id))
            
        if self.product_id:
            domain.append(('product_id', '=', self.product_id.id))

        if self.workcenter_id:
            domain.append(('workcenter_id', '=', self.workcenter_id.id))

        manufacturing_orders = self.env['mrp.production'].search(domain)

        all_orders = []

        for order in manufacturing_orders:
            order_data = {
                # "mo_name": order.name,
                "product": order.product_id.name,
                "quantity": order.product_qty,
                "workcenter": order.workcenter_id.name if order.workcenter_id else "N/A",
                "state": order.state,
                "progress": f"{order.qty_produced / order.product_qty * 100:.2f}%" if order.product_qty else "0%",
                "date_planned_start": order.date_planned_start,
                "date_planned_finished": order.date_planned_finished,
                "take_time": (datetime.now().date() - order.date_planned_start.date()).days if order.date_planned_start else 0,
                "left_time": (order.date_planned_finished.date() - datetime.now().date()).days if order.date_planned_finished else 0,
            }

            all_orders.append(order_data)

        print(f'Manufacturing Orders -> {all_orders}')
        
        return {"all_orders": all_orders}

    def generate_manufacturing_by_order_report(self):
        return self.env.ref('sales_report.manufacturing_report_action').report_action(self)
