# # from odoo import models, fields

# # class ResCompany(models.Model):
# #     _inherit = 'res.company'

# #     business_type = fields.Selection([
# #         ('service', 'Service'),
# #         ('wholesale_retail', 'Wholesale/Retail'),
# #         ('manufacturing', 'Manufacturing'),
# #     ], string="Business Type", default="service")

# # from odoo import models, api, fields, _

# # class AccountMove(models.Model):
# #     _inherit = 'account.move'

# #     @api.model
# #     def _add_inventory_and_cost_of_sales_lines(self):
# #         """
# #         Adds inventory and cost of sales journal items to the move lines 
# #         if the company's business type is 'manufacturing' or 'wholesale/retail'.
# #         """
# #         for move in self:
# #             # Ensure this applies to customer invoices
# #             if move.move_type == 'out_invoice' and move.company_id.business_type in ['manufacturing', 'wholesale_retail']:
# #                 # Get accounts for inventory and cost of sales
# #                 inventory_account = self.env['account.account'].search([('code', '=', '120234')], limit=1)
# #                 cost_of_sales_account = self.env['account.account'].search([('code', '=', '511100')], limit=1)

# #                 if not inventory_account or not cost_of_sales_account:
# #                     raise ValueError(_('Please configure Inventory and Cost of Sales accounts.'))

# #                 # Calculate inventory and cost of sales amounts
# #                 inventory_value = sum(move.invoice_line_ids.mapped('product_id.standard_price'))  # Adjust as per your costing method
# #                 cost_of_sales_value = inventory_value  # Adjust logic if necessary

# #                 if inventory_value and cost_of_sales_value:
# #                     # Add inventory credit line
# #                     self.env['account.move.line'].create({
# #                         'move_id': move.id,
# #                         'account_id': inventory_account.id,
# #                         'name': _('Inventory Value'),
# #                         'debit': 0.0,
# #                         'credit': inventory_value,
# #                     })

# #                     # Add cost of sales debit line
# #                     self.env['account.move.line'].create({
# #                         'move_id': move.id,
# #                         'account_id': cost_of_sales_account.id,
# #                         'name': _('Cost of Sales'),
# #                         'debit': cost_of_sales_value,
# #                         'credit': 0.0,
# #                     })

# #     def action_post(self):
# #         """
# #         Override the action_post to add inventory and cost of sales lines
# #         if the company's business type is 'manufacturing' or 'wholesale/retail'.
# #         """
# #         res = super(AccountMove, self).action_post()
# #         self._add_inventory_and_cost_of_sales_lines()
# #         return res



# from odoo import models, fields, api, _

# class ResCompany(models.Model):
#     _inherit = 'res.company'

#     business_type = fields.Selection([
#         ('service', 'Service'),
#         ('wholesale_retail', 'Wholesale/Retail'),
#         ('manufacturing', 'Manufacturing'),
#     ], string="Business Type", default="service")


# class AccountMove(models.Model):
#     _inherit = 'account.move'

#     def _prepare_inventory_and_cost_of_sales_lines(self):
#         """
#         Prepares inventory and cost of sales journal items to be added to the move lines
#         if the company's business type is 'manufacturing' or 'wholesale/retail'.
#         """
#         move_lines = []
#         for move in self:
#             if move.move_type == 'out_invoice' and move.company_id.business_type in ['manufacturing', 'wholesale_retail']:
#                 # Get accounts for inventory and cost of sales
#                 inventory_account = self.env['account.account'].search([('code', '=', '120234')], limit=1)
#                 cost_of_sales_account = self.env['account.account'].search([('code', '=', '511100')], limit=1)

#                 if not inventory_account or not cost_of_sales_account:
#                     raise ValueError(_('Please configure Inventory and Cost of Sales accounts.'))

#                 # Calculate inventory and cost of sales amounts
#                 inventory_value = 0.0
#                 cost_of_sales_value = 0.0
#                 for line in move.invoice_line_ids:
#                     inventory_value += line.product_id.standard_price * line.quantity
#                     cost_of_sales_value += line.product_id.standard_price * line.quantity

#                 if inventory_value and cost_of_sales_value:
#                     # Add inventory credit line
#                     for line in move.invoice_line_ids:
#                         move_lines.append({
#                             'move_id': move.id,
#                             'name': _('Inventory Value'),
#                             'debit': 0.0,
#                             'credit': inventory_value,
#                             'account_id': inventory_account.id,
#                             'product_id': line.product_id.id,
#                         })

#                         # Add cost of sales debit line
#                         move_lines.append({
#                             'move_id': move.id,
#                             'name': _('Cost of Sales'),
#                             'debit': cost_of_sales_value,
#                             'credit': 0.0,
#                             'account_id': cost_of_sales_account.id,
#                             'product_id': line.product_id.id,
#                         })
#         return move_lines

#     def action_post(self):
#         """
#         Override the action_post to add inventory and cost of sales lines
#         if the company's business type is 'manufacturing' or 'wholesale/retail'.
#         """
#         res = super(AccountMove, self).action_post()
#         for move in self:
#             move_lines = move._prepare_inventory_and_cost_of_sales_lines()
#             if move_lines:
#                 self.env['account.move.line'].create(move_lines)
#         return res

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class ResCompany(models.Model):
    _inherit = 'res.company'

    business_type = fields.Selection([
        ('service', 'Service'),
        ('wholesale_retail', 'Wholesale/Retail'),
        ('manufacturing', 'Manufacturing'),
    ], string="Business Type", default="service")


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _prepare_inventory_and_cost_of_sales_lines(self):
        """
        Prepares inventory and cost of sales journal items to be added to the move lines
        if the company's business type is 'manufacturing' or 'wholesale/retail'.
        """
        move_lines = []
        for move in self:
            if move.move_type == 'out_invoice' and move.company_id.business_type in ['manufacturing', 'wholesale_retail']:
                # Get accounts for inventory and cost of sales
                inventory_account = self.env['account.account'].search([('code', '=', '120234')], limit=1)
                cost_of_sales_account = self.env['account.account'].search([('code', '=', '511100')], limit=1)

                if not inventory_account or not cost_of_sales_account:
                    raise ValueError(_('Please configure Inventory and Cost of Sales accounts.'))

                for line in move.invoice_line_ids:
                    # Calculate values for inventory and cost of sales
                    inventory_value = line.product_id.standard_price * line.quantity
                    cost_of_sales_value = inventory_value  # Assuming inventory and cost of sales are the same

                    _logger.info(f"Processing line for product {line.product_id.name}:")
                    _logger.info(f"Inventory Value: {inventory_value}, Cost of Sales Value: {cost_of_sales_value}")

                    # Add inventory credit line
                    move_lines.append({
                        'move_id': move.id,
                        'name': _('Inventory Value'),
                        'debit': 0.0,
                        'credit': inventory_value,
                        'account_id': inventory_account.id,
                        'product_id': line.product_id.id,
                    })

                    # Add cost of sales debit line
                    move_lines.append({
                        'move_id': move.id,
                        'name': _('Cost of Sales'),
                        'debit': cost_of_sales_value,
                        'credit': 0.0,
                        'account_id': cost_of_sales_account.id,
                        'product_id': line.product_id.id,
                    })

                    _logger.info(f"Move Lines Added for Product {line.product_id.name}: {move_lines}")

        return move_lines

    def action_post(self):
        """
        Override the action_post to add inventory and cost of sales lines
        if the company's business type is 'manufacturing' or 'wholesale/retail'.
        """
        res = super(AccountMove, self).action_post()
        for move in self:
            move_lines = move._prepare_inventory_and_cost_of_sales_lines()
            if move_lines:
                self.env['account.move.line'].create(move_lines)
                _logger.info(f"Inventory and Cost of Sales Lines Created for Move {move.name}")
        return res
