# purchase_tender/models/purchase_tender.py

from odoo import models, fields, api,_
from odoo.exceptions import ValidationError
class PurchaseTender(models.Model):
    _name = 'purchase.tender'
    _description = 'Purchase Tender'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True, copy=False, default=lambda self: _('New'), readonly=True)
    product_id = fields.Many2one('product.product', string='Product', required=True, readonly=True)
    request_id = fields.Char(string='Purchase Request', readonly=True)
    tender_status = fields.Boolean(string="Status", default=False)
    tender_line_ids = fields.One2many('purchase.tender.line', 'purchase_tender_id', string='Tender Lines')
    tender_date= fields.Date(string="Created Date", default=fields.Date.today())
    manual_winner = fields.Boolean(string='Manual Winner', default=False)
    tender_commute_ids = fields.Many2many(
        'tender.valuation.commute',
        string='Tender Commutes',
        required=False
    )
    evaluation_ids = fields.One2many('tender.line.evaluation', 'tender_id', string='Evaluations')

    vendor_comparison_ids = fields.One2many(
        'vendor.price.comparison',  # Related model
        'tender_id',  # Reverse Many2one field in vendor.price.comparison
        string="Vendor Price Comparison"
    )

    purchase_order_count = fields.Integer(string='Purchase Order Count', compute='_compute_purchase_order_count')


    # New fields for local limits
    use_local_limits = fields.Boolean(string='Use Local Limits', default=False)
    local_response_i_q_t = fields.Float(string="Response I/Q/T (%)", default=5)
    local_product_quality = fields.Float(string="Product Quality (%)", default=25)
    local_warranty = fields.Float(string="Warranty (%)", default=10)
    local_price_value = fields.Float(string="Price Value (%)", default=25)
    local_delivery_performance = fields.Float(string="Delivery Performance (%)", default=10)
    local_credit_facility = fields.Float(string="Credit Facility (%)", default=10)
    local_stock_availability = fields.Float(string="Stock Availability (%)", default=5)
    local_reputation_past_experience = fields.Float(string="Reputation Past Experience (%)", default=10)

    comeetes= fields.Many2many('hr.employee', string="Comeetes")
    memo = fields.Binary(string="Memo", attachment=True)
    memo_filename = fields.Char(string="Memo Filename")
    vendor_ids = fields.Many2many(
        'res.partner',
        string='Vendors',
        compute='_compute_vendor_ids',
        store=True
    )

    @api.depends('tender_line_ids.partner_id')
    def _compute_vendor_ids(self):
        for record in self:
            record.vendor_ids = record.tender_line_ids.mapped('partner_id')

    @api.constrains(
        'local_response_i_q_t', 'local_product_quality', 'local_warranty', 'local_price_value', 
        'local_delivery_performance', 'local_credit_facility', 'local_stock_availability', 
        'local_reputation_past_experience'
    )
    def _check_individual_and_total_limits(self):
        for record in self:
            # Check individual fields are no more than 100
            fields_to_check = [
                record.local_response_i_q_t, record.local_product_quality, record.local_warranty,
                record.local_price_value, record.local_delivery_performance, record.local_credit_facility,
                record.local_stock_availability, record.local_reputation_past_experience
            ]
            if any(field > 100 for field in fields_to_check):
                raise ValidationError("Each field value must be no more than 100.")

            # Check total does not exceed 100
            if sum(fields_to_check) > 100:
                raise ValidationError("The sum of all fields must not exceed 100.")


    def _compute_purchase_order_count(self):
        for rec in self:
            rec.purchase_order_count = self.env['purchase.order'].search_count([('ref', '=', rec.request_id)])
            if not rec.tender_status:
                rec.purchase_order_count=0

    def purchase_order_action(self):

        return {
            'type': 'ir.actions.act_window',
            'name': 'Purchase Order',
            'res_model': 'purchase.order',
            'domain': [('ref', '=', self.request_id)],
            'view_mode': 'tree,form',
            'target': 'current'
        }

    # def _compute_tender_status(self):
    #     for rec in self:
            
    #         # purchase_orders = self.env['purchase.order'].search([('ref', '=', rec.request_id)])
    #         # if len(purchase_orders)>0:
    #         #     rec.tender_status = True
    #         # else:
    #         #     rec.tender_status = False

    def create_purchase_order(self):
        for tender in self:
            # Check if any purchase orders already exist for this tender
            purchase_orders = self.env['purchase.order'].search([('ref', '=', tender.request_id)])

            # Continue only if no purchase orders exist for this tender
            if not purchase_orders:
                # Get all lines where winner is True
                winning_lines = tender.tender_line_ids.filtered(lambda line: line.winner)

                # Check if there are winning lines to create POs
                if winning_lines:
                    for line in winning_lines:
                        # Prepare the order values for each purchase order
                        order_vals = {
                            'partner_id': line.partner_id.id,  # Vendor for this line
                            'ref': tender.request_id,
                            'tender_status':True,
                            'order_line': [
                                (0, 0, {
                                    'tender_id': tender.id,
                                    'product_id': tender.product_id.id,  # Product from the tender
                                    'name': tender.product_id.name or 'Description',
                                    'product_qty': line.product_qty,  # Quantity from the line
                                    'price_unit': line.price_unit,  # Price from the winning line
                                })
                            ]
                        }

                        self.env['purchase.order'].create(order_vals)
                        self.tender_status=True
            else:
                winning_lines = tender.tender_line_ids.filtered(lambda line: line.winner)
                for po in purchase_orders:
                    for w in winning_lines:
                        if w.partner_id.id == po.partner_id.id:
                            
                                po_lines = po.order_line
                                po_lines.create({
                                    'product_id': tender.product_id.id,
                                    'product_qty': w.product_qty,
                                    'price_unit': w.price_unit,
                                    'order_id':po.id
                                })
                        else:
                            order_vals = {
                            'partner_id': w.partner_id.id,  
                            'ref': tender.request_id,
                            'tender_status':True,
                            'order_line': [
                                (0, 0, {
                                    'tender_id': tender.id,
                                    'product_id': tender.product_id.id,  
                                    'name': tender.product_id.name or 'Description',
                                    'product_qty': w.product_qty, 
                                    'price_unit': w.price_unit,  
                                        })
                                    ]
                                }

                            self.env['purchase.order'].create(order_vals)
                self.tender_status=True


                        


    @api.model
    def create(self, vals):
        if vals.get('name', ('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('purchase.tender') or _('New')
            res = super(PurchaseTender, self).create(vals)
            all_commute_records = self.env['tender.valuation.commute'].search([])
            res.tender_commute_ids = [(6, 0, all_commute_records.ids)]
            return res
    def action_create_transit_records(self):
        """
        Button action to create/update transit records.
        """
        # Call the create_transit_records method on tender lines
        self.tender_line_ids.create_transit_records()
        # return {
        #     'type': 'ir.actions.client',
        #     'tag': 'reload',
        # }


class PurchaseTenderLine(models.Model):
    _name = 'purchase.tender.line'
    _description = 'Purchase Tender Line'

    purchase_tender_id = fields.Many2one('purchase.tender', string='Tender')
    partner_id = fields.Many2one('res.partner', string='Vendor')
    representative_id = fields.Many2many('hr.employee', string='Representative', required=False)
    product_qty = fields.Float(string='Quantity', required=True)
    product_uom = fields.Many2one('uom.uom', string='UOM')
    price_unit = fields.Float(string='Unit Price')
    price_value = fields.Float(compute='_compute_price_value', string="Financial Value")
   
    product_quality = fields.Float(string="Quality (%)")
    # warranty = fields.Float(string="Equipment and Tools")
    # delivery_performance = fields.Float(string="Range of service Offered ")
    # credit_facility = fields.Float(string="Refference Testimonials & Reptuation ")
    # stock_availability = fields.Float(string="safty protocols")
    # reputation_past_experience = fields.Float(string="Documentation")
    total_score = fields.Float(string="Total (100%)")
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string="End Date")
    state= fields.Date(string="State")
    evaluation_ids = fields.One2many('tender.line.evaluation', 'tender_line_id', string='Evaluations')

    warranty = fields.Float(string="Equipment and Tools (10%)", compute='_compute_average_warranty', store=True)
    delivery_performance = fields.Float(string="Range of service offfered (10%)", compute='_compute_average_delivery_performance', store=True)
    credit_facility = fields.Float(string="Safty Protocols (5%)", compute='_compute_average_credit_facility', store=True)
    stock_availability = fields.Float(string="Documentation (5%)", compute='_compute_average_stock_availability', store=True)
    reputation_past_experience = fields.Float(string="Year of experiance (10%)", compute='_compute_average_reputation', store=True)
    response_i_q_t = fields.Float(string="Reference Testimonials & Reputation (10%)", compute='_compute_average_response_i_q_t', store=True)

    # New field to check if this line has the lowest unit price
    winner = fields.Boolean(string='Winner', compute='_compute_is_winner', store=True, readonly=False)

    # New computed field
    average_committee_score = fields.Float(string="Average Committee Score", compute="_compute_average_committee_score", store=True)

    @api.depends('evaluation_ids.response_i_q_t')
    def _compute_average_response_i_q_t(self):
        for record in self:
            values = record.evaluation_ids.mapped('response_i_q_t')
            record.response_i_q_t = sum(values) / len(values) if values else 0

    @api.depends('evaluation_ids')
    def _compute_average_scores(self):
        """
        Compute the average scores for all evaluation criteria across all users.
        """
        for record in self:
            evaluations = record.evaluation_ids
            record.warranty = sum(evaluations.mapped('warranty')) / len(evaluations) if evaluations else 0
            record.delivery_performance = sum(evaluations.mapped('delivery_performance')) / len(evaluations) if evaluations else 0
            record.credit_facility = sum(evaluations.mapped('credit_facility')) / len(evaluations) if evaluations else 0
            record.stock_availability = sum(evaluations.mapped('stock_availability')) / len(evaluations) if evaluations else 0
            record.reputation_past_experience = sum(evaluations.mapped('reputation_past_experience')) / len(evaluations) if evaluations else 0

    @api.depends('evaluation_ids.warranty')
    def _compute_average_warranty(self):
        for record in self:
            values = record.evaluation_ids.mapped('warranty')
            record.warranty = sum(values) / len(values) if values else 0

    @api.depends('evaluation_ids.delivery_performance')
    def _compute_average_delivery_performance(self):
        for record in self:
            values = record.evaluation_ids.mapped('delivery_performance')
            record.delivery_performance = sum(values) / len(values) if values else 0

    @api.depends('evaluation_ids.credit_facility')
    def _compute_average_credit_facility(self):
        for record in self:
            values = record.evaluation_ids.mapped('credit_facility')
            record.credit_facility = sum(values) / len(values) if values else 0

    @api.depends('evaluation_ids.stock_availability')
    def _compute_average_stock_availability(self):
        for record in self:
            values = record.evaluation_ids.mapped('stock_availability')
            record.stock_availability = sum(values) / len(values) if values else 0

    @api.depends('evaluation_ids.reputation_past_experience')
    def _compute_average_reputation(self):
        for record in self:
            values = record.evaluation_ids.mapped('reputation_past_experience')
            record.reputation_past_experience = sum(values) / len(values) if values else 0


    @api.depends('partner_id')
    def _compute_average_committee_score(self):
        for record in self:
            if not record.partner_id:
                record.average_committee_score = 0
                continue
            
            # Fetch all committee scores for the vendor
            scores = self.env['vendor.evaluation.score'].search([
                ('vendor_id', '=', record.partner_id.id)
            ]).mapped('score')
            
            record.average_committee_score = sum(scores) / len(scores) if scores else 0
    @api.model
    def create(self, vals):
        record = super(PurchaseTenderLine, self).create(vals)
        record._update_vendor_comparison()
        return record

    def write(self, vals):
        res = super(PurchaseTenderLine, self).write(vals)
        self._update_vendor_comparison()
        return res

    def _update_vendor_comparison(self):
        """Update Vendor Price Comparison when a tender line is changed"""
        if self.purchase_tender_id:
            self.env['vendor.price.comparison'].update_vendor_comparison(self.purchase_tender_id.id)

    @api.onchange(
        'response_i_q_t', 'product_quality', 'price_value', 
        'delivery_performance', 'credit_facility', 
        'stock_availability', 'reputation_past_experience'
    )
    def _onchange_field_validation(self):
        # Validate each field to ensure values are between 0 and 100
        for record in self:
            for field_name in [
                'response_i_q_t', 'product_quality', 'price_value', 
                'delivery_performance', 'credit_facility', 
                'stock_availability', 'reputation_past_experience']:
                field_value = getattr(record, field_name)
                if field_value < 0 or field_value > 100:
                    # Reset the field value to 0 and give a warning
                    setattr(record, field_name, 0)
                    return {
                        'warning': {
                            'title': "Validation Error",
                            'message': f"{field_name.replace('_', ' ').title()} must be between 0 and 100."
                        }
                    }
                    

    # @api.depends('price_unit', 'purchase_tender_id.tender_line_ids.price_unit')
    # def _compute_price_value(self):
    #     for record in self:
    #         tender = record.purchase_tender_id
    #         if not tender:
    #             record.price_value = 0  # Default value if no tender is linked
    #             continue
            
    #         # Determine price weight value
    #         price_weight_value = (
    #             tender.local_price_value if tender.use_local_limits 
    #             else float(self.env['ir.config_parameter'].sudo().get_param('purchase.price_value', default=25.0))
    #         )
            
    #         # Get all tender lines and filter out invalid price_unit
    #         tender_lines = tender.tender_line_ids
    #         price_units = [line.price_unit for line in tender_lines if line.price_unit is not None]
            
    #         if not price_units:
    #             for line in tender_lines:
    #                 line.price_value = 0  # Set default if no valid price_units
    #             continue
            
    #         # Find the minimum price unit
    #         min_price_unit = min(price_units)
            
    #         # Compute price_value for each tender line
    #         for line in tender_lines:
    #             if min_price_unit > 0:
    #                 line.price_value = (min_price_unit / line.price_unit) * price_weight_value
    #             else:
    #                 line.price_value = price_weight_value  # Default if min_price_unit is zero
    @api.depends('price_unit', 'purchase_tender_id.tender_line_ids.price_unit')
    def _compute_price_value(self):
        for record in self:
            tender = record.purchase_tender_id
            if not tender:
                record.price_value = 0  # Default value if no tender is linked
                continue

            # Set price weight value to 50 (fixed)
            price_weight_value = 50

            # Get all tender lines and filter out invalid price_unit
            tender_lines = tender.tender_line_ids
            price_units = [line.price_unit for line in tender_lines if line.price_unit is not None]

            if not price_units:
                for line in tender_lines:
                    line.price_value = 0  # Set default if no valid price_units
                continue

            # Find the minimum price unit
            min_price_unit = min(price_units)

            # Compute price_value for each tender line
            for line in tender_lines:
                if min_price_unit > 0:
                    line.price_value = (min_price_unit / line.price_unit) * price_weight_value
                else:
                    line.price_value = price_weight_value  # Default if min_price_unit is zero
    # # @api.depends(
    # # 'price_value', 'response_i_q_t', 'product_quality', 'warranty',
    # # 'delivery_performance', 'credit_facility', 'stock_availability', 'reputation_past_experience'
    # # )
    # # def _compute_is_winner(self):
    # #     for record in self:
    # #         tender = record.purchase_tender_id

    # #         # Define weight values
    # #         if tender.use_local_limits:
    # #             weights = {
    # #                 'response_i_q_t': tender.local_response_i_q_t,
    # #                 'warranty': tender.local_warranty,
    # #                 'product_quality': tender.local_product_quality,
    # #                 'delivery_performance': tender.local_delivery_performance,
    # #                 'credit_facility': tender.local_credit_facility,
    # #                 'stock_availability': tender.local_stock_availability,
    # #                 'reputation_past_experience': tender.local_reputation_past_experience,
    # #             }
    # #         else:
    # #             config = self.env['ir.config_parameter'].sudo()
    # #             weights = {
    # #                 'response_i_q_t': float(config.get_param('purchase.response_i_q_t', default=5.0)),
    # #                 'warranty': float(config.get_param('purchase.warranty', default=10.0)),
    # #                 'product_quality': float(config.get_param('purchase.product_quality', default=25.0)),
    # #                 'delivery_performance': float(config.get_param('purchase.delivery_performance', default=10.0)),
    # #                 'credit_facility': float(config.get_param('purchase.credit_facility', default=10.0)),
    # #                 'stock_availability': float(config.get_param('purchase.stock_availability', default=5.0)),
    # #                 'reputation_past_experience': float(config.get_param('purchase.reputation_past_experience', default=10.0)),
    # #             }

    # #         # Gather all warranties from tender lines
    # #         tender_lines = record.mapped('purchase_tender_id.tender_line_ids')
    # #         warranties = [line.warranty for line in tender_lines if line.warranty is not None]

    # #         # Compute max warranty (prevent division by zero)
    # #         max_warranty = max(warranties, default=1)

    # #         # Calculate total score for the record
    # #         record.total_score = (
    # #             record.price_value +
    # #             ((record.response_i_q_t / 100) * weights['response_i_q_t']) +
    # #             ((record.warranty / (max_warranty if max_warranty != 0 else 1)) *  weights['warranty']) +  # Prevent division by zero
    # #             ((record.product_quality / 100) * weights['product_quality']) +
    # #             ((record.delivery_performance / 100) * weights['delivery_performance']) +
    # #             ((record.credit_facility / 100) * weights['credit_facility']) +
    # #             ((record.stock_availability / 100) * weights['stock_availability']) +
    # #             ((record.reputation_past_experience / 100) * weights['reputation_past_experience'])
    # #         )

    # #     # Determine highest-scoring lines
    # #     for tender in self.mapped('purchase_tender_id'):
    # #         tender_lines = tender.tender_line_ids
    # #         if not tender_lines:
    # #             continue

    # #         highest_score = max((line.total_score for line in tender_lines), default=None)
    # #         highest_score_lines = [line for line in tender_lines if line.total_score == highest_score]

    # #         for line in tender_lines:
    # #             if tender.manual_winner:
    # #                 continue
    # #             line.winner = (line in highest_score_lines)

    # @api.depends(
    #     'response_i_q_t', 'product_quality', 'warranty',
    #     'delivery_performance', 'credit_facility', 'stock_availability', 'reputation_past_experience'
    # )
    # def _compute_is_winner(self):
    #     for record in self:
    #         tender = record.purchase_tender_id

    #         # Define weight values
    #         if tender.use_local_limits:
    #             weights = {
    #                 'response_i_q_t': tender.local_response_i_q_t,
    #                 'warranty': tender.local_warranty,
    #                 'product_quality': tender.local_product_quality,
    #                 'delivery_performance': tender.local_delivery_performance,
    #                 'credit_facility': tender.local_credit_facility,
    #                 'stock_availability': tender.local_stock_availability,
    #                 'reputation_past_experience': tender.local_reputation_past_experience,
    #             }
    #         else:
    #             config = self.env['ir.config_parameter'].sudo()
    #             weights = {
    #                 'response_i_q_t': float(config.get_param('purchase.response_i_q_t', default=5.0)),
    #                 'warranty': float(config.get_param('purchase.warranty', default=10.0)),
    #                 'product_quality': float(config.get_param('purchase.product_quality', default=25.0)),
    #                 'delivery_performance': float(config.get_param('purchase.delivery_performance', default=10.0)),
    #                 'credit_facility': float(config.get_param('purchase.credit_facility', default=10.0)),
    #                 'stock_availability': float(config.get_param('purchase.stock_availability', default=5.0)),
    #                 'reputation_past_experience': float(config.get_param('purchase.reputation_past_experience', default=10.0)),
    #             }

    #         # Gather all warranties from tender lines
    #         tender_lines = record.mapped('purchase_tender_id.tender_line_ids')
    #         warranties = [line.warranty for line in tender_lines if line.warranty is not None]

    #         # Compute max warranty (prevent division by zero)
    #         max_warranty = max(warranties, default=1)

    #         # Calculate total score for the record (excluding price_value)
    #         record.total_score = (
    #             ((record.response_i_q_t / 100) * weights['response_i_q_t']) +
    #             ((record.warranty / (max_warranty if max_warranty != 0 else 1)) * weights['warranty']) +  # Prevent division by zero
    #             ((record.product_quality / 100) * weights['product_quality']) +
    #             ((record.delivery_performance / 100) * weights['delivery_performance']) +
    #             ((record.credit_facility / 100) * weights['credit_facility']) +
    #             ((record.stock_availability / 100) * weights['stock_availability']) +
    #             ((record.reputation_past_experience / 100) * weights['reputation_past_experience'])
    #         )

    #     # Determine highest-scoring lines
    #     for tender in self.mapped('purchase_tender_id'):
    #         tender_lines = tender.tender_line_ids
    #         if not tender_lines:
    #             continue

    #         highest_score = max((line.total_score for line in tender_lines), default=None)
    #         highest_score_lines = [line for line in tender_lines if line.total_score == highest_score]

    #         for line in tender_lines:
    #             if tender.manual_winner:
    #                 continue
    #             line.winner = (line in highest_score_lines)

    @api.depends(
    'price_value', 'response_i_q_t', 'product_quality', 'warranty',
    'delivery_performance', 'credit_facility', 'stock_availability', 'reputation_past_experience'
                )
    def _compute_is_winner(self):
        for record in self:
            tender = record.purchase_tender_id

            # Define weight values
            if tender.use_local_limits:
                weights = {
                    'response_i_q_t': tender.local_response_i_q_t,
                    'warranty': tender.local_warranty,
                    'product_quality': tender.local_product_quality,
                    'delivery_performance': tender.local_delivery_performance,
                    'credit_facility': tender.local_credit_facility,
                    'stock_availability': tender.local_stock_availability,
                    'reputation_past_experience': tender.local_reputation_past_experience,
                }
            else:
                config = self.env['ir.config_parameter'].sudo()
                weights = {
                    'response_i_q_t': float(config.get_param('purchase.response_i_q_t', default=5.0)),
                    'warranty': float(config.get_param('purchase.warranty', default=10.0)),
                    'product_quality': float(config.get_param('purchase.product_quality', default=25.0)),
                    'delivery_performance': float(config.get_param('purchase.delivery_performance', default=10.0)),
                    'credit_facility': float(config.get_param('purchase.credit_facility', default=10.0)),
                    'stock_availability': float(config.get_param('purchase.stock_availability', default=5.0)),
                    'reputation_past_experience': float(config.get_param('purchase.reputation_past_experience', default=10.0)),
                }

            # Normalize weights to ensure they sum to 50%
            total_weight = sum(weights.values())
            normalized_weights = {key: (value / total_weight) * 50 for key, value in weights.items()}

            # Gather all warranties from tender lines
            tender_lines = record.mapped('purchase_tender_id.tender_line_ids')
            warranties = [line.warranty for line in tender_lines if line.warranty is not None]

            # Compute max warranty (prevent division by zero)
            max_warranty = max(warranties, default=1)

            # Calculate total score for the record
            record.total_score = (
                (record.price_value / 100) * 50 +  # Price value takes 50%
                ((record.response_i_q_t / 100) * normalized_weights['response_i_q_t']) +
                ((record.warranty / (max_warranty if max_warranty != 0 else 1)) * normalized_weights['warranty']) +
                ((record.product_quality / 100) * normalized_weights['product_quality']) +
                ((record.delivery_performance / 100) * normalized_weights['delivery_performance']) +
                ((record.credit_facility / 100) * normalized_weights['credit_facility']) +
                ((record.stock_availability / 100) * normalized_weights['stock_availability']) +
                ((record.reputation_past_experience / 100) * normalized_weights['reputation_past_experience'])
            )

        # Determine highest-scoring lines
        for tender in self.mapped('purchase_tender_id'):
            tender_lines = tender.tender_line_ids
            if not tender_lines:
                continue

            highest_score = max((line.total_score for line in tender_lines), default=None)
            highest_score_lines = [line for line in tender_lines if line.total_score == highest_score]

            for line in tender_lines:
                if tender.manual_winner:
                    continue
                line.winner = (line in highest_score_lines)

    @api.model
    def create_transit_records(self):
        # Get the winning vendors for the current tender
        # winning_vendors = self.filtered('winner').mapped('partner_id.id')

        # Unlink previous lines for the same product and request_id, but exclude winning vendors
        previous_transits = self.env['purchase.tender.transit'].search([
            ('request_id', '=', self.purchase_tender_id.request_id),
            # ('vendor_id', 'not in', winning_vendors),
        ])
        for transit in previous_transits:
            transit_lines = transit.transit_line_ids.filtered(lambda l: l.product_id.id == self.purchase_tender_id.product_id.id)
            if transit_lines:
                transit_lines.unlink()
            if transit.product_count == 0:
                transit.unlink()    
        # Process winner lines to create or update transit records
        for line in self.filtered('winner'):
            # Fetch or create a transit record for the current vendor and tender
            transit_record = self.env['purchase.tender.transit'].search([
                ('vendor_id', '=', line.partner_id.id),
                ('request_id', '=', self.purchase_tender_id.request_id),
            ], limit=1)

            if not transit_record:
                transit_record = self.env['purchase.tender.transit'].create({
                    'vendor_id': line.partner_id.id,
                    'request_id': self.purchase_tender_id.request_id,
                })

            # Add a new line to the transit record
            self.env['purchase.tender.transit.line'].create({
                'transit_id': transit_record.id,
                'tender_id': self.purchase_tender_id.id,
                'product_id': self.purchase_tender_id.product_id.id,
                'product_qty': line.product_qty,
                'product_uom': line.product_uom.id,
                'price_unit': line.price_unit,
            })
    
    @api.model
    def create(self, vals):
        record = super(PurchaseTenderLine, self).create(vals)
        if record.purchase_tender_id:
            self.env['tender.line.evaluation'].synchronize_evaluations(record.purchase_tender_id.id)
        return record

    def write(self, vals):
        res = super(PurchaseTenderLine, self).write(vals)
        if self.purchase_tender_id:
            self.env['tender.line.evaluation'].synchronize_evaluations(self.purchase_tender_id.id)
        return res

class PurchaseOrderTender(models.Model):
    _inherit = 'purchase.order'

    tender_status = fields.Boolean( string='Purchase Tender Status', default=False)
    ref = fields.Char(string="Ref", readonly=True)
    transit_id = fields.Many2one('purchase.tender.transit', string="Transit Ref", readonly=True)
    partner_id = fields.Many2one('res.partner', required=True)

    product_ids = fields.Many2many(
        'product.product',
        string='Allowed Products',
        compute='_compute_product_ids',
        store=False,
    )

    @api.onchange('partner_id')
    def _compute_product_ids(self):
        for order in self:
            supplierinfos = self.env['product.supplierinfo'].search([('partner_id', '=', self.partner_id.id)])
            order.product_ids = supplierinfos.mapped('product_id')

    
class PurchaseOrderTender(models.Model):
    _inherit = 'purchase.order.line'

    tender_id = fields.Many2one('purchase.tender', string='Purchase Tender')


class TenderLineEvaluation(models.Model):
    _name = 'tender.line.evaluation'
    _description = 'Tender Line Evaluation'

    tender_id = fields.Many2one('purchase.tender', string='Tender', required=True)
    tender_line_id = fields.Many2one(
        'purchase.tender.line', 
        string='Tender Line', 
        required=True,
        domain="[('purchase_tender_id', '=', tender_id)]"
    )
    vendor_id = fields.Many2one(
        'res.partner', 
        string='Vendor',
        related='tender_line_id.partner_id',
        store=True,
        readonly=True
    )
    user_id = fields.Many2one('res.users', string='User', required=True, default=lambda self: self.env.user)

    # Evaluation Criteria
    warranty = fields.Float(string="Equipment and Tools (10%)")
    delivery_performance = fields.Float(string="Range of service offered (10%)")
    credit_facility = fields.Float(string="Safety Protocols (5%)")
    stock_availability = fields.Float(string="Documentation (5%)")
    reputation_past_experience = fields.Float(string="Year of experience (10%)")
    response_i_q_t = fields.Float(string="Reference Testimonials & Reputation (10%)")
    @api.model
    def synchronize_evaluations(self, tender_id):
        """
        Synchronize evaluations for all vendors in purchase.tender.line
        and create records for all internal users.
        """
        tender_lines = self.env['purchase.tender.line'].search([('purchase_tender_id', '=', tender_id)])
        internal_users = self.env['res.users'].search([('share', '=', False)])  # Fetch all internal users
        evaluation_obj = self.env['tender.line.evaluation']

        for line in tender_lines:
            if not line.partner_id:  # Skip if vendor is missing
                continue

            for user in internal_users:
                # Check if an evaluation exists for the current user
                existing_entry = evaluation_obj.search([
                    ('tender_id', '=', tender_id),
                    ('vendor_id', '=', line.partner_id.id),
                    ('tender_line_id', '=', line.id),
                    ('user_id', '=', user.id),
                ], limit=1)

                if not existing_entry:
                    # Create a new evaluation for the user
                    evaluation_obj.create({
                        'tender_id': tender_id,
                        'tender_line_id': line.id,
                        'vendor_id': line.partner_id.id,
                        'user_id': user.id,
                    })

    @api.constrains(
        'warranty', 'delivery_performance', 'reputation_past_experience',
        'credit_facility', 'stock_availability','response_i_q_t'
    )

    def _check_field_limits(self):
        """
        Ensure that the specified fields do not exceed their maximum values.
        """
        for record in self:
            # Fields with a maximum value of 10
            if record.warranty > 10:
                raise ValidationError(_("The value for 'Equipment and Tools (10%)' cannot exceed 10."))
            if record.delivery_performance > 10:
                raise ValidationError(_("The value for 'Range of service offered (10%)' cannot exceed 10."))
            if record.reputation_past_experience > 10:
                raise ValidationError(_("The value for 'Year of experience (10%)' cannot exceed 10."))

            if record.response_i_q_t > 10:
                raise ValidationError(_("Reference Testimonials & Reputation' cannot exceed 10."))


            # Fields with a maximum value of 5
            if record.credit_facility > 5:
                raise ValidationError(_("The value for 'Safety Protocols (5%)' cannot exceed 5."))
            if record.stock_availability > 5:
                raise ValidationError(_("The value for 'Documentation (5%)' cannot exceed 5."))

    @api.model
    def create(self, vals):
        """
        Override the create method to ensure evaluations are created
        for all internal users when a new record is created.
        """
        record = super(TenderLineEvaluation, self).create(vals)
        if 'tender_id' in vals:
            self.synchronize_evaluations(vals['tender_id'])
        return record
from odoo import models, fields, api

class VendorPriceComparison(models.Model):
    _name = 'vendor.price.comparison'
    _description = 'Vendor Price Comparison'

    tender_id = fields.Many2one('purchase.tender', string="Purchase Tender", required=True)  
    vendor_id = fields.Many2one(
        'res.partner', string="Vendor", 
        domain=[('supplier_rank', '>', 0)], required=True
    )
    price = fields.Float(string="Price Per Unit", required=True)
    quantity = fields.Float(string="Quantity", required=True)
    total_price = fields.Float(string="Total Price", compute="_compute_total_price", store=True)
    comparison_score = fields.Float(string="Comparison Score", compute="_compute_comparison_score", store=True)

    _sql_constraints = [
        ('unique_vendor_tender', 'unique(tender_id, vendor_id)', 
         'Each vendor can have only one price entry per tender!')
    ]

    @api.depends('price', 'quantity')
    def _compute_total_price(self):
        """Calculate total price (price * quantity)"""
        for record in self:
            record.total_price = record.price * record.quantity

    @api.depends('price', 'tender_id')
    def _compute_comparison_score(self):
        """Calculate comparison score based on price range in the tender"""
        for record in self:
            vendor_prices = self.search([('tender_id', '=', record.tender_id.id)]).mapped('price')

            if vendor_prices:
                lowest_price = min(vendor_prices)
                highest_price = max(vendor_prices)
                record.comparison_score = (lowest_price / highest_price) * 50 if highest_price > 0 else 0
            else:
                record.comparison_score = 0
    @api.model
    def update_vendor_comparison(self, tender_id):
        """
        Automatically updates or creates Vendor Price Comparison records 
        based on PurchaseTenderLine data.
        """
        tender_lines = self.env['purchase.tender.line'].search([('purchase_tender_id', '=', tender_id)])
        vendor_comparison_obj = self.env['vendor.price.comparison']

        for line in tender_lines:
            if not line.partner_id:  # Skip if vendor is missing
                continue
            
            # Search for an existing vendor entry
            existing_entry = vendor_comparison_obj.search([
                ('tender_id', '=', tender_id),
                ('vendor_id', '=', line.partner_id.id)
            ], limit=1)

            if existing_entry:
                existing_entry.write({
                    'price': line.price_unit,
                    'quantity': line.product_qty,
                })
            else:
                vendor_comparison_obj.create({
                    'tender_id': tender_id,
                    'vendor_id': line.partner_id.id,
                    'price': line.price_unit,
                    'quantity': line.product_qty,
                })


# class PurchaseTender(models.Model):
#     _inherit = 'purchase.tender'
#     # _inherit = ['mail.thread', 'mail.activity.mixin']

#     # Existing fields...
#     committee_user_ids = fields.One2many(
#         'res.users', 
#         compute='_compute_committee_users', 
#         string="Committee Users"
#     )

#     @api.depends()
#     def _compute_committee_users(self):
#         for record in self:
#             # Fetch users with is_committee = True
#             record.committee_user_ids = self.env['res.users'].search([('is_committee', '=', True)])