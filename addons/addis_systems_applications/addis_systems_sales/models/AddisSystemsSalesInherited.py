from odoo import fields, models, api


class AddisSystemsSalesOrderLineInherited(models.Model):
    _inherit = 'sale.order.line'

    single_tax = fields.Many2one('account.tax', context={'active_test': False}, check_company=True)

    def write(self, vals):
        if 'single_tax' in vals and vals['single_tax']:
            self.tax_id = None
            vals['tax_id'] = [(4, int(vals['single_tax']))]
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'single_tax' in vals and vals['single_tax']:
                vals['tax_id'] = [(4, int(vals['single_tax']))]

        return super().create(vals_list)