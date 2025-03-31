from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import pytz


class CommunicationDetails(models.Model):
    _name = 'communication.details'
    _description = 'Communication Details'

    name = fields.Char(string='Person\'s Name', required=True)
    email = fields.Char(string='Email Address', required=True)
    phone = fields.Char(string='Phone Number', required=True)
    event_id = fields.Many2one('event.management', string='Event', ondelete='cascade')

class Event(models.Model):
    _name = 'event.management'
    _description = 'Event Management'

    # Currency field to store currency information

    currency_id = fields.Many2one(
        string="Currency", help="This is the Currency used",
        related='pricelist_id.currency_id',
        depends=['pricelist_id.currency_id'],
    )

    communication_ids = fields.One2many('communication.details', 'event_id', string='Communication Details')

    @api.constrains('communication_ids')
    def _check_communication_details(self):
        for record in self:
            if not record.communication_ids:
                raise models.ValidationError("At least one communication detail must be provided.")
    booking_id = fields.Many2one('room.booking', string="room booking")
    name = fields.Char(string="Event Name", required=True)
    start_date = fields.Datetime(string="Start Date")
    end_date = fields.Datetime(string="End Date")
    guest_count = fields.Integer(string="Number of Guests")
    service_ids = fields.Many2many('event.service', string="Available Services")

    need_food = fields.Boolean(default=False, string="Need Food",
                               help="Check if Food is to be added with the Booking")
    need_drinks = fields.Boolean(default=False, string="Need Drinks",
                                 help="Check if Drinks are to be added with the Booking")
    need_service = fields.Boolean(default=False, string="Need Service",
                                  help="Check if a Service is to be added with the Booking")
    need_fleet = fields.Boolean(default=False, string="Need Vehicle",
                                help="Check if a Fleet to be"
                                     " added with the Booking")
    need_room = fields.Boolean(default=False, string="Need Room",
                               help="Check if a Room is to be added with the Booking")

    company_id = fields.Many2one('res.company', string="Company",
                                 help="Choose the Company",
                                 required=True, index=True,
                                 default=lambda self: self.env.company)
    partner_id = fields.Many2one('res.partner', string="Customer",
                                 help="Customers of hotel",
                                 required=True, index=True, tracking=1,
                                 domain="[('type', '!=', 'private'),"
                                        " ('company_id', 'in', "
                                        "(False, company_id))]")

    date_order = fields.Datetime(
        string="Order Date",
        required=True, copy=False,
        help="Creation date of draft/sent orders,"
             " Confirmation date of confirmed orders.",
        default=fields.Datetime.now)
    checkin_date = fields.Datetime(string="Check In",
                                   help="Date of Checkin",
                                   default=fields.Datetime.now())
    checkout_date = fields.Datetime(string="Check Out",
                                    help="Date of Checkout",
                                    states={"draft": [("readonly", False)]},
                                    default=fields.Datetime.now() + timedelta(
                                        hours=23, minutes=59, seconds=59))
    invoice_button_visible = fields.Boolean(string='Invoice Button Display',
                                            help="Invoice button will be "
                                                 "visible if this button is "
                                                 "True")
    invoice_status = fields.Selection(
        selection=[('no_invoice', 'Nothing To Invoice'),
                   ('to_invoice', 'To Invoice'),
                   ('invoiced', 'Invoiced'),
                   ], string="Invoice Status",
        help="Status of the Invoice",
        default='no_invoice', tracking=True)
    hotel_invoice_id = fields.Many2one("account.move",
                                       string="Invoice",
                                       help="Indicates the invoice",
                                       copy=False)


    # Overall totals for all services
    amount_untaxed = fields.Monetary(
        string="Untaxed Amount",
        help="Total untaxed amount for all services (rooms, food, drinks).",
        compute='_compute_amount_untaxed',
        store=True,
        currency_field='currency_id'
    )
    amount_tax = fields.Monetary(
        string="Taxes",
        help="Total taxes for all services (rooms, food, drinks).",
        compute='_compute_amount_untaxed',
        store=True,
        currency_field='currency_id'
    )
    amount_total = fields.Monetary(
        string="Total Amount",
        help="Total amount (taxed) for all services (rooms, food, drinks).",
        compute='_compute_amount_untaxed',
        store=True,
        currency_field='currency_id'
    )

    # Monetary fields for individual services
    amount_untaxed_food = fields.Monetary(
        string="Food Untaxed",
        help="Untaxed Amount for Food",
        compute='_compute_amount_untaxed',
        store=True,
        currency_field='currency_id'
    )
    amount_untaxed_room = fields.Monetary(
        string="Room Untaxed",
        help="Untaxed Amount for Room",
        compute='_compute_amount_untaxed',
        store=True,
        currency_field='currency_id'
    )
    amount_untaxed_drinks = fields.Monetary(
        string="Drinks Untaxed",
        help="Untaxed Amount for Drinks",
        compute='_compute_amount_untaxed',
        store=True,
        currency_field='currency_id'
    )

    amount_taxed_food = fields.Monetary(
        string="Food Taxed",
        help="Taxed Amount for Food",
        compute='_compute_amount_untaxed',
        store=True,
        currency_field='currency_id'
    )
    amount_taxed_room = fields.Monetary(
        string="Room Taxed",
        help="Taxed Amount for Room",
        compute='_compute_amount_untaxed',
        store=True,
        currency_field='currency_id'
    )
    amount_taxed_drinks = fields.Monetary(
        string="Drinks Taxed",
        help="Taxed Amount for Drinks",
        compute='_compute_amount_untaxed',
        store=True,
        currency_field='currency_id'
    )

    amount_total_food = fields.Monetary(
        string="Total Food",
        help="Total Amount for Food",
        compute='_compute_amount_untaxed',
        store=True,
        currency_field='currency_id'
    )
    amount_total_room = fields.Monetary(
        string="Total Room",
        help="Total Amount for Room",
        compute='_compute_amount_untaxed',
        store=True,
        currency_field='currency_id'
    )
    amount_total_drinks = fields.Monetary(
        string="Total Drinks",
        help="Total Amount for Drinks",
        compute='_compute_amount_untaxed',
        store=True,
        currency_field='currency_id'
    )
    amount_untaxed_fleet = fields.Monetary(string="Amount Untaxed",
                                           help="Untaxed amount for Fleet",
                                           compute='_compute_amount_untaxed',
                                           tracking=5)
    amount_taxed_fleet = fields.Monetary(string="Fleet Tax",
                                         compute='_compute_amount_untaxed',
                                         help="Tax for Fleet", tracking=5)
    amount_total_fleet = fields.Monetary(string="Total Amount for Fleet",
                                         compute='_compute_amount_untaxed',
                                         help="This is the Total Amount for "
                                              "Fleet", tracking=5)
    amount_untaxed_service= fields.Monetary(string="Amount Untaxed",
                                            help="Untaxed amount for Service",
                                            compute='_compute_amount_untaxed',
                                            )
    amount_taxed_service = fields.Monetary(string="Service Tax",help="Tax for Service", compute='_compute_amount_untaxed',)
    amount_total_service = fields.Monetary(string="Total Amount for Service", compute='_compute_amount_untaxed', help="This is the Total Amount for Service",)


    duration_visible = fields.Float(string="Duration",
                                    help="A dummy field for Duration")
    is_checkin = fields.Boolean(default=False, string="Is Checkin",
                                help="sets to True if the room is occupied")


    # Notebook for Room Service
    event_room_line_ids = fields.One2many(
        'event.room.booking.line',
        'event_id',
        string="Room Details",
        help="Room details provided to the Customer and will be included in the main invoice."
    )

    # Notebook for Drinks Service

    event_food_order_line_ids= fields.One2many("event.food.booking.line",   "event_id", string="Food",
                                               help="Food details provided to Customer and it will be included in the main invoice.")
    drinks_line_ids = fields.One2many(
        'event.drinks.line',
        'event_id',
        string="Drinks Details"
    )
    event_vehicle_line_ids = fields.One2many("event.fleet.booking.line",
                                             "event_id",
                                             string="Vehicle",
                                             help="Hotel fleet reservation detail.")
    event_service_line_ids = fields.One2many("event.service.booking.line",
                                       "event_id",
                                       string="Service",
                                       help="Hotel services details provided to"
                                            "Customer and it will included in "
                                            "the main Invoice.")








    user_id = fields.Many2one(
        comodel_name='res.partner',
        string="Invoice Address",
        compute='_compute_user_id',
        help="Sets the User automatically", required=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=',"
               " company_id)]")
    pricelist_id = fields.Many2one(
        comodel_name='product.pricelist',
        string="Pricelist",
        compute='_compute_pricelist_id',
        store=True, readonly=False,

        tracking=1,
        help="If you change the pricelist, only newly added lines"
             " will be affected.")

    duration = fields.Integer(string="Duration in Days",
                              help="Number of days which will automatically "
                                   "count from the check-in and check-out "
                                   "date.", )
    state = fields.Selection(selection=[('draft', 'Draft'),
                                        ('reserved', 'Reserved'),
                                        ('check_in', 'Check In'),
                                        ('check_out', 'Check Out'),
                                        ('cancel', 'Cancelled'),
                                        ('done', 'Done')], string='State',
                             help="State of the Booking",
                             default='draft', tracking=True)


    invoice_count = fields.Integer(compute='_compute_invoice_count',
                                   string="Invoice "
                                          "Count",
                                   help="The number of invoices created")
    account_move = fields.Integer(string='Invoice Id',
                                  help="Id of the invoice created")

    def unlink(self):
        for rec in self:
            if rec.state != 'cancel' and rec.state != 'draft':
                raise ValidationError('Cannot delete the Booking. Cancel the Booking ')
        return super().unlink()

    @api.model
    def create(self, vals_list):
        """Sequence Generation"""
        if vals_list.get('name', 'New') == 'New':
            vals_list['name'] = self.env['ir.sequence'].next_by_code(
                'room.booking')
        return super().create(vals_list)

    @api.depends('partner_id')
    def _compute_user_id(self):
        """Computes the User id"""
        for order in self:
            order.user_id = \
                order.partner_id.address_get(['invoice'])[
                    'invoice'] if order.partner_id else False

    def _compute_invoice_count(self):
        """Compute the invoice count"""
        for record in self:
            record.invoice_count = self.env['account.move'].search_count(
                [('ref', '=', self.name)])

    @api.depends('partner_id')
    def _compute_pricelist_id(self):
        """Computes PriceList"""
        for order in self:
            if not order.partner_id:
                order.pricelist_id = False
                continue
            order = order.with_company(order.company_id)
            order.pricelist_id = order.partner_id.property_product_pricelist


    @api.depends('event_room_line_ids.price_subtotal', 'event_room_line_ids.price_tax',
                 'event_room_line_ids.price_total',
                 'event_food_order_line_ids.price_subtotal',
                 'event_food_order_line_ids.price_tax',
                 'event_food_order_line_ids.price_total',
                 'drinks_line_ids.price_subtotal',
                 'drinks_line_ids.price_tax',
                 'drinks_line_ids.price_total',
                 'event_service_line_ids.price_subtotal',
                 'event_service_line_ids.price_tax', 'event_service_line_ids.price_total',
                 'event_vehicle_line_ids.price_subtotal',
                 'event_vehicle_line_ids.price_tax', 'event_vehicle_line_ids.price_total',

                 )
    def _compute_amount_untaxed(self, flag=False):
        """Compute the total amounts of the Sale Order"""
        amount_untaxed_room = 0.0
        amount_untaxed_food = 0.0
        amount_untaxed_fleet = 0.0
        amount_untaxed_drinks= 0.0

        amount_untaxed_service = 0.0
        amount_taxed_room = 0.0
        amount_taxed_food = 0.0
        amount_taxed_fleet = 0.0
        amount_taxed_drinks= 0.0

        amount_taxed_service = 0.0
        amount_total_room = 0.0
        amount_total_food = 0.0
        amount_total_fleet = 0.0
        amount_total_drinks= 0.0

        amount_total_service = 0.0
        room_lines = self.event_room_line_ids
        food_lines = self.event_food_order_line_ids
        service_lines = self.event_service_line_ids
        fleet_lines = self.event_vehicle_line_ids
        drinks_lines=self.drinks_line_ids

        booking_list = []
        account_move_line = self.env['account.move.line'].search_read(
            domain=[('ref', '=', self.name),
                    ('display_type', '!=', 'payment_term')],
            fields=['name', 'quantity', 'price_unit', 'product_type'], )
        for rec in account_move_line:
            del rec['id']
        if room_lines:
            amount_untaxed_room += sum(room_lines.mapped('price_subtotal'))
            amount_taxed_room += sum(room_lines.mapped('price_tax'))
            amount_total_room += sum(room_lines.mapped('price_total'))
            for room in room_lines:
                booking_dict = {'name': room.room_id.name,
                                'quantity': room.uom_qty,
                                'price_unit': room.price_unit,
                                'product_type': 'room'}
                if booking_dict not in account_move_line:
                    if not account_move_line:
                        booking_list.append(booking_dict)
                    else:
                        for rec in account_move_line:
                            if rec['product_type'] == 'room':
                                if booking_dict['name'] == rec['name'] and \
                                        booking_dict['price_unit'] == rec[
                                    'price_unit'] and booking_dict['quantity'] \
                                        != rec['quantity']:
                                    booking_list.append(
                                        {'name': room.room_id.name,
                                         "quantity": booking_dict[
                                                         'quantity'] - rec[
                                                         'quantity'],
                                         "price_unit": room.price_unit,
                                         "product_type": 'room'})
                                else:
                                    booking_list.append(booking_dict)
                    if flag:
                        room.booking_line_visible = True
        if food_lines:
            for food in food_lines:
                booking_list.append(self.create_list(food))
            amount_untaxed_food += sum(food_lines.mapped('price_subtotal'))
            amount_taxed_food += sum(food_lines.mapped('price_tax'))
            amount_total_food += sum(food_lines.mapped('price_total'))
        if drinks_lines:
            for drinks in drinks_lines:
                booking_list.append(self.create_list(drinks))
            amount_untaxed_drinks += sum(drinks_lines.mapped('price_subtotal'))
            amount_taxed_drinks += sum(drinks_lines.mapped('price_tax'))
            amount_total_drinks += sum(drinks_lines.mapped('price_total'))


        if service_lines:
            for service in service_lines:
                booking_list.append(self.create_list(service))
            amount_untaxed_service += sum(
                service_lines.mapped('price_subtotal'))
            amount_taxed_service += sum(service_lines.mapped('price_tax'))
            amount_total_service += sum(service_lines.mapped('price_total'))
        if fleet_lines:
            for fleet in fleet_lines:
                booking_list.append(self.create_list(fleet))
            amount_untaxed_fleet += sum(fleet_lines.mapped('price_subtotal'))
            amount_taxed_fleet += sum(fleet_lines.mapped('price_tax'))
            amount_total_fleet += sum(fleet_lines.mapped('price_total'))

        for rec in self:
            rec.amount_untaxed = amount_untaxed_food + amount_untaxed_room + \
                                 amount_untaxed_fleet + \
                                  amount_untaxed_drinks + amount_untaxed_service
            rec.amount_untaxed_food = amount_untaxed_food
            rec.amount_untaxed_room = amount_untaxed_room
            rec.amount_untaxed_fleet = amount_untaxed_fleet
            rec.amount_untaxed_drinks= amount_untaxed_drinks

            rec.amount_untaxed_service = amount_untaxed_service
            rec.amount_tax = (amount_taxed_food + amount_taxed_room
                              + amount_taxed_fleet+
                              amount_taxed_drinks + amount_taxed_service)
            rec.amount_taxed_food = amount_taxed_food
            rec.amount_taxed_room = amount_taxed_room
            rec.amount_taxed_fleet = amount_taxed_fleet
            rec.amount_taxed_drinks=amount_taxed_drinks

            rec.amount_taxed_service = amount_taxed_service
            rec.amount_total = (amount_total_food + amount_total_room
                                + amount_total_fleet+ amount_total_drinks
                                + amount_total_service)
            rec.amount_total_food = amount_total_food
            rec.amount_total_room = amount_total_room
            rec.amount_total_fleet = amount_total_fleet
            rec.amount_total_drinks= amount_total_drinks

            rec.amount_total_service = amount_total_service
        return booking_list

    @api.onchange('need_food')
    def _onchange_need_food(self):
        """Unlink Food Booking Line if Need Food is false"""
        if not self.need_food and self.event_food_order_line_ids:
            for food in self.event_food_order_line_ids:
                food.unlink()

    @api.onchange('need_drinks')
    def _onchange_need_drinks(self):
        """Unlink Food Booking Line if Need Food is false"""
        if not self.need_drinks and self.drinks_line_ids:
            for food in self.drinks_line_ids:
                food.unlink()

    @api.onchange('need_service')
    def _onchange_need_service(self):
        """Unlink Service Booking Line if Need Service is False"""
        if not self.need_service and self.event_service_line_ids:
            for serv in self.event_service_line_ids:
                serv.unlink()

    @api.onchange('need_fleet')
    def _onchange_need_fleet(self):
        """Unlink Fleet Booking Line if Need Fleet is False"""
        if not self.need_fleet:
            if self.event_vehicle_line_ids:
                for fleet in self.event.vehicle_line_ids:
                    fleet.unlink()

    # @api.onchange('need_event')
    # def _onchange_need_event(self):
    #     """Unlink Event Booking Line if Need Event is False"""
    #     if not self.need_event:
    #         if self.event_line_ids:
    #             for event in self.event_line_ids:
    #                 event.unlink()

    @api.onchange('event_food_order_line_ids', 'event_room_line_ids',
                  'event_service_line_ids', 'event_vehicle_line_ids','drinks_line_ids')
    def _onchange_room_line_ids(self):
        """Invokes the Compute amounts function"""
        self._compute_amount_untaxed()
        self.invoice_button_visible = False

    @api.constrains("event_room_line_ids")
    def _check_duplicate_folio_room_line(self):
        """
        This method is used to validate the room_lines.
        ------------------------------------------------
        @param self: object pointer
        @return: raise warning depending on the validation
        """
        for record in self:
            # Create a set of unique ids
            ids = set()
            for line in record.event_room_line_ids:
                if line.room_id.id in ids:
                    raise ValidationError(
                        _(
                            """Room Entry Duplicates Found!, """
                            """You Cannot Book "%s" Room More Than Once!"""
                        )
                        % line.room_id.name
                    )
                ids.add(line.room_id.id)

    def create_list(self, line_ids):
        """Returns a Dictionary containing the Booking line Values"""
        account_move_line = self.env['account.move.line'].search_read(
            domain=[('ref', '=', self.name),
                    ('display_type', '!=', 'payment_term')],
            fields=['name', 'quantity', 'price_unit', 'product_type'], )
        for rec in account_move_line:
            del rec['id']
        booking_dict = {}
        for line in line_ids:
            name = ""
            product_type = ""
            if line_ids._name == 'event.food.booking.line':
                name = line.food_id.name
                product_type = 'food'
            elif line_ids._name == 'event.fleet.booking.line':
                name = line.fleet_id.name
                product_type = 'fleet'
            elif line_ids._name == 'event.service.booking.line':
                name = line.service_id.name
                product_type = 'service'
            elif line_ids._name == 'event.drinks.line':
                name = line.drink_id.name
                product_type = 'drinks'
            booking_dict = {'name': name,
                            'quantity': line.uom_qty,
                            'price_unit': line.price_unit,
                            'product_type': product_type}


        return booking_dict

    def action_reserve(self):
        """Button Reserve Function"""
        if self.state == 'reserved':
            message = _("Room Already Reserved.")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'warning',
                    'message': message,
                    'next': {'type': 'ir.actions.act_window_close'},
                }
            }
        if self.event_room_line_ids:
            for room in self.event_room_line_ids:
                room.room_id.write({
                    'status': 'reserved',
                })
                room.room_id.is_room_avail = False
            self.write({"state": "reserved"})
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'success',
                    'message': "Rooms reserved Successfully!",
                    'next': {'type': 'ir.actions.act_window_close'},
                }
            }
        raise ValidationError(_("Please Enter Room Details"))

    def action_cancel(self):
        """
        @param self: object pointer
        """
        if self.event_room_line_ids:
            for room in self.event_room_line_ids:
                room.room_id.write({
                    'status': 'available',
                })
                room.room_id.is_room_avail = True
        self.write({"state": "cancel"})

    # def action_maintenance_request(self):
    #     """
    #     Function that handles the maintenance request
    #     """
    #     room_list = []
    #     for rec in self.room_line_ids.room_id.ids:
    #         room_list.append(rec)
    #     if room_list:
    #         room_id = self.env['hotel.room'].search([
    #             ('id', 'in', room_list)])
    #         self.env['maintenance.request'].sudo().create({
    #             'date': fields.Date.today(),
    #             'state': 'draft',
    #             'type': 'room',
    #             'room_maintenance_ids': room_id.ids,
    #         })
    #         self.maintenance_request_sent = True
    #         return {
    #             'type': 'ir.actions.client',
    #             'tag': 'display_notification',
    #             'params': {
    #                 'type': 'success',
    #                 'message': "Maintenance Request Sent Successfully",
    #                 'next': {'type': 'ir.actions.act_window_close'},
    #             }
    #         }
    #     raise ValidationError(_("Please Enter Room Details"))
    #
    def action_done(self):
        """Button action_confirm function"""
        for rec in self.env['account.move'].search(
                [('ref', '=', self.name)]):
            if rec.payment_state != 'not_paid':
                self.write({"state": "done"})
                self.is_checkin = False
                if self.event_room_line_ids:
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'type': 'success',
                            'message': "Booking Checked Out Successfully!",
                            'next': {'type': 'ir.actions.act_window_close'},
                        }
                    }
            raise ValidationError(_('Your Invoice is Due for Payment.'))
        self.write({"state": "done"})

    def action_checkout(self):
        """Button action_heck_out function"""
        self.write({"state": "check_out"})
        for room in self.event_room_line_ids:
            room.room_id.write({
                'status': 'available',
                'is_room_avail': True
            })
            room.write({'checkout_date': datetime.today()})

    def action_invoice(self):
        """Method for creating invoice and handling stock movements"""
        if not self.event_room_line_ids:
            raise ValidationError(_("Please Enter Room Details"))

        # Compute booking details
        booking_list = self._compute_amount_untaxed(True)
        if booking_list:
            # Create Invoice
            account_move = self.env["account.move"].create([{
                'move_type': 'out_invoice',
                'invoice_date': fields.Date.today(),
                'partner_id': self.partner_id.id,
                'ref': self.name,
            }])
            for rec in booking_list:
                account_move.invoice_line_ids.create([{
                    'name': rec['name'],
                    'quantity': rec['quantity'],
                    'price_unit': rec['price_unit'],
                    'move_id': account_move.id,
                    'price_subtotal': rec['quantity'] * rec['price_unit'],
                    'product_type': rec['product_type'],
                }])

            # Create Stock Picking for the Invoice
            picking = self.env['stock.picking'].create({
                'partner_id': self.partner_id.id,
                'picking_type_id': self.env.ref('stock.picking_type_out').id,  # Outgoing shipment
                'location_id': self.env.ref('stock.stock_location_stock').id,  # WH/Stock
                'location_dest_id': self.partner_id.property_stock_customer.id,  # Customer location
                'origin': self.name,
            })

            # Create Stock Moves for Products
            for rec in booking_list:
                product = self.env['product.product'].search([('name', '=', rec['name'])], limit=1)
                if product:
                    self.env['stock.move'].create({
                        'name': rec['name'],
                        'product_id': product.id,
                        'product_uom_qty': rec['quantity'],
                        'product_uom': product.uom_id.id,
                        'picking_id': picking.id,
                        'location_id': self.env.ref('stock.stock_location_stock').id,  # WH/Stock
                        'location_dest_id': self.partner_id.property_stock_customer.id,  # Customer location
                    })

            # Confirm and Validate the Stock Picking
            picking.action_confirm()
            picking.action_assign()
            picking.button_validate()

            # Mark Invoice as Created
            self.write({'invoice_status': "invoiced"})
            self.invoice_button_visible = True

            # Return the Invoice Form View
            return {
                'type': 'ir.actions.act_window',
                'name': 'Invoices',
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'account.move',
                'view_id': self.env.ref('account.view_move_form').id,
                'res_id': account_move.id,
                'context': "{'create': False}"
            }

    def action_view_invoices(self):
        """Method for Returning invoice View"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoices',
            'view_mode': 'tree,form',
            'view_type': 'tree,form',
            'res_model': 'account.move',
            'domain': [('ref', '=', self.name)],
            'context': "{'create': False}"
        }

    def action_checkin(self):
        """
        @param self: object pointer
        """
        if not self.event_room_line_ids:
            raise ValidationError(_("Please Enter Room Details"))
        else:
            for room in self.event_room_line_ids:
                room.room_id.write({
                    'status': 'occupied',
                })
                room.room_id.is_room_avail = False
            self.write({"state": "check_in"})
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'success',
                    'message': "Booking Checked In Successfully!",
                    'next': {'type': 'ir.actions.act_window_close'},
                }
            }

    # def get_details(self):
    #     """ Returns different counts for displaying in dashboard"""
    #     today = datetime.today()
    #     tz_name = self.env.user.tz
    #     today_utc = pytz.timezone('UTC').localize(today,
    #                                               is_dst=False)
    #     context_today = today_utc.astimezone(pytz.timezone(tz_name))
    #     total_room = self.env['hotel.room'].search_count([])
    #     check_in = self.env['room.booking'].search_count(
    #         [('state', '=', 'check_in')])
    #     available_room = self.env['hotel.room'].search(
    #         [('status', '=', 'available')])
    #     reservation = self.env['room.booking'].search_count(
    #         [('state', '=', 'reserved')])
    #     check_outs = self.env['room.booking'].search([])
    #     check_out = 0
    #     staff = 0
    #     for rec in check_outs:
    #         for room in rec.room_line_ids:
    #             if room.checkout_date.date() == context_today.date():
    #                 check_out += 1
    #         """staff"""
    #         staff = self.env['res.users'].search_count(
    #             [('groups_id', 'in',
    #               [self.env.ref('hotel_management_odoo.hotel_group_admin').id,
    #                self.env.ref(
    #                    'hotel_management_odoo.cleaning_team_group_head').id,
    #                self.env.ref(
    #                    'hotel_management_odoo.cleaning_team_group_user').id,
    #                self.env.ref(
    #                    'hotel_management_odoo.hotel_group_reception').id,
    #                self.env.ref(
    #                    'hotel_management_odoo.maintenance_team_group_leader').id,
    #                self.env.ref(
    #                    'hotel_management_odoo.maintenance_team_group_user').id
    #                ])])
    #     total_vehicle = self.env['fleet.vehicle.model'].search_count([])
    #     available_vehicle = total_vehicle - self.env[
    #         'fleet.booking.line'].search_count(
    #         [('state', '=', 'check_in')])
    #     total_event = self.env['event.event'].search_count([])
    #     pending_event = self.env['event.event'].search([])
    #     pending_events = 0
    #     today_events = 0
    #     for pending in pending_event:
    #         if pending.date_end >= fields.datetime.now():
    #             pending_events += 1
    #         if pending.date_end.date() == fields.date.today():
    #             today_events += 1
    #     food_items = self.env['lunch.product'].search_count([])
    #     food_order = len(self.env['food.booking.line'].search([]).filtered(
    #         lambda r: r.booking_id.state not in ['check_out', 'cancel',
    #                                              'done']))
    #     """total Revenue"""
    #     total_revenue = 0
    #     today_revenue = 0
    #     pending_payment = 0
    #     for rec in self.env['account.move'].search(
    #             [('payment_state', '=', 'paid')]):
    #         if rec.ref:
    #             if 'BOOKING' in rec.ref:
    #                 total_revenue += rec.amount_total
    #                 if rec.date == fields.date.today():
    #                     today_revenue += rec.amount_total
    #     for rec in self.env['account.move'].search(
    #             [('payment_state', '=', 'not_paid')]):
    #         if rec.ref:
    #             if 'BOOKING' in rec.ref:
    #                 pending_payment += rec.amount_total
    #     return {
    #         'total_room': total_room,
    #         'available_room': len(available_room),
    #         'staff': staff,
    #         'check_in': check_in,
    #         'reservation': reservation,
    #         'check_out': check_out,
    #         'total_vehicle': total_vehicle,
    #         'available_vehicle': available_vehicle,
    #         'total_event': total_event,
    #         'today_events': today_events,
    #         'pending_events': pending_events,
    #         'food_items': food_items,
    #         'food_order': food_order,
    #         'total_revenue': round(total_revenue, 2),
    #         'today_revenue': round(today_revenue, 2),
    #         'pending_payment': round(pending_payment, 2),
    #         'currency_symbol': self.env.user.company_id.currency_id.symbol,
    #         'currency_position': self.env.user.company_id.currency_id.position
    #     }
