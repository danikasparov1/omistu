from odoo import models, fields, api
from odoo.exceptions import ValidationError

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.constrains('price_unit', 'product_uom_qty')
    def _check_price_and_quantity(self):
        for line in self:
            if line.price_unit < 0:
                raise ValidationError("The Unit Price must be greater than or equal to 0.")
            if line.product_uom_qty < 0:
                raise ValidationError("The Quantity must be greater than or equal to 0.")