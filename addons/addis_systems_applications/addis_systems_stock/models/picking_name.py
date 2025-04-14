from odoo import SUPERUSER_ID, _, api, Command, fields, models
class ProductProduct(models.Model):
    _name = 'product.product'
    _inherit = 'product.product'
    customer_request_line_ids = fields.One2many('customer.product.request.line', 'product_id', string="CR Lines")
