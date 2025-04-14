from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    warehouse_id = fields.Many2one('stock.warehouse', default=lambda self: self.env.user.allowed_warehouses_ids[0].id if self.env.user.allowed_warehouses_ids else False)

    
    @api.model
    def create(self, values):
        sale_order = super(SaleOrder, self).create(values)
        
        orders = []
        for order_line in sale_order.order_line:
            product = order_line.product_id
            ordered_quantity = order_line.product_uom_qty
            available_quantity = self.env['stock.quant']._get_available_quantity(product, sale_order.warehouse_id.view_location_id, allow_negative=False)
            
            if ordered_quantity > available_quantity:
                orders.append({
                    "product": product.name,
                    "requested": ordered_quantity,
                    "available": available_quantity
                })
        
        if orders:
            message = "".join([f"""\n\t\t{order['product']} | {order['requested']} is requested > {order['available']} is available, """ for order in orders])
            raise ValidationError(_(f"The ordered quantity for product/s exceeds available quantity in {sale_order.warehouse_id.name}. {message}"))
        
        return sale_order



    