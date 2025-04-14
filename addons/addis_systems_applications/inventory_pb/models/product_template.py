from odoo import models, fields, api


# class ProductTemplate(models.Model):
#     _inherit = 'product.product'
    
    
#     default_warehouse_id = fields.Many2one(
#         'stock.warehouse', string="Default Warehouse",
#         # required=True, 
#         domain="[('company_id', '=', self.env.company.id)]",
#         help="This warehouse will be pre-selected when creating a new product or suggesting a warehouse in stock operations."
#     )
    


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    default_warehouse_id = fields.Many2one(
        'stock.warehouse', string="Default Warehouse",
        store=True,
        # required=True, 
        help="This warehouse will be pre-selected when creating a new product or suggesting a warehouse in stock operations."
    )
    
    # on_hand = fields.Float(string='On Hand', compute='_compute_on_hand')

    
    # def _compute_on_hand(self):
    #     for record in self:
    #         record.on_hand = 550

            # current_user = self.env.user
            # allowed_warehouses = current_user.allowed_warehouses_ids.ids
            
            # if allowed_warehouses: 
            #     # for warehouse in allowed_warehouses:
            #     #     warehouse_id = warehouse.id
            #     quants = self.env['stock.quant'].search([
            #         ('product_id', '=', record.id),
            #         ('warehouse_id', 'in', allowed_warehouses)
            #     ])
            #     total_quantity = sum(quant.quantity for quant in quants)
            #     record.on_hand = total_quantity
                
            # else:
            #     record.on_hand = 0


# class ProductProduct(models.Model):
#     _inherit = 'product.product'
    
#     default_warehouse_id = fields.Many2one(
#         'stock.warehouse', string="Default Warehouse",
#         store=True,
#         # required=True, 
#         domain="[('company_id', '=', self.env.company.id)]",
#         help="This warehouse will be pre-selected when creating a new product or suggesting a warehouse in stock operations."
#     )
    