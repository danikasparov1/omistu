from odoo import models, fields, api

class EventDrinksLine(models.Model):
    _name = 'event.drinks.line'
    _description = 'Tea Line'

    _rec_name = 'drink_id'  # Set to the drink_id field

    drink_id = fields.Many2one(
        'product.template',
        string="Drinks",
        help="Indicates the Drink Product",
        domain="[('pos_categ_id.name', 'in', ['Drinks', 'Soft Drinks'])]"
    )
    event_id = fields.Many2one('event.management', string="Event")
    date = fields.Date(string="Date")
    session = fields.Selection(
        [('morning', 'Morning'), ('afternoon', 'Afternoon')],
        string="Session"
    )
    uom_qty = fields.Float(string="Qty", default=1,
                           help="The quantity converted into the UoM used by "
                                "the product")
    price_unit = fields.Float(related='drink_id.list_price', string='Price',
                              digits='Product Price',
                              help="The price of the selected food item.")
    no_of_users = fields.Integer(string="Number of Users")
    # price_per_user = fields.Float(string="Price per User")
    tax_ids = fields.Many2many(
        'account.tax',
        'event_drinks_order_line_taxes_rel',
        'event_drinks_line_id', 'tax_id',
        string='Taxes',
        help="Taxes applied to this drinks line.",
        domain=[('type_tax_use', '=', 'sale')]
    )
    currency_id = fields.Many2one(
        related='event_id.currency_id',
        string="Currency",
        help="The currency used for pricing."
    )
    price_subtotal = fields.Float(
        string="Subtotal",
        compute='_compute_price_subtotal', help="Total Price Excluding Tax",
        store=True)
    price_tax = fields.Float(
        string="Total Tax",
        compute='_compute_price_subtotal', help="Tax Amount",
        store=True)
    price_total = fields.Float(
        string="Total",
        compute='_compute_price_subtotal', help="Total Price Including Tax",
        store=True)

    @api.depends('no_of_users')
    def _compute_uom_qty(self):
        """
        Compute the quantity field (uom_qty) based on no_of_users.
        """
        for line in self:
            line.uom_qty = line.no_of_users

    @api.depends('price_per_user')
    def _compute_price_unit(self):
        """
        Compute the unit price (price_unit) based on price_per_user.
        """
        for line in self:
            line.price_unit = line.price_per_user

    @api.depends('uom_qty', 'price_unit', 'tax_ids')
    def _compute_price_subtotal(self):
        """
        Compute the amounts of the room booking line.
        """
        for line in self:
            tax_results = self.env['account.tax']._compute_taxes(
                [line._convert_to_tax_base_line_dict()])
            totals = list(tax_results['totals'].values())[0]
            amount_untaxed = totals['amount_untaxed']
            amount_tax = totals['amount_tax']
            line.update({
                'price_subtotal': amount_untaxed,
                'price_tax': amount_tax,
                'price_total': amount_untaxed + amount_tax,
            })
            if self.env.context.get('import_file',
                                    False) and not self.env.user. \
                    user_has_groups('account.group_account_manager'):
                line.tax_id.invalidate_recordset(
                    ['invoice_repartition_line_ids'])

    def _convert_to_tax_base_line_dict(self):
        """ Convert the current record to a dictionary in order to use the
        generic taxes computation method
        defined on account.tax.
        :return: A python dictionary.
        """
        self.ensure_one()
        return self.env['account.tax']._convert_to_tax_base_line_dict(
            self,
            # partner=self.booking_id.partner_id,
            currency=self.currency_id,
            taxes=self.tax_ids,
            price_unit=self.price_unit,
            quantity=self.uom_qty,
            price_subtotal=self.price_subtotal,
        )
