from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo import _

_STATES = [
    ("draft", "Draft"),
    ("to_approve", "To Approve"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
]

class StoreRequest(models.Model):
    _name = "store.request"
    _description = "Store Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    name = fields.Char(
        string="Request Reference",
        required=True,
        default=lambda self: _("New"),
        tracking=True,
    )
    requested_by = fields.Many2one(
        comodel_name="res.users",
        string="Requested By",
        default=lambda self: self.env.user,
        required=True,
        tracking=True,
    )
    date_requested = fields.Date(
        string="Request Date",
        default=fields.Date.context_today,
        required=True,
        tracking=True,
    )
    description = fields.Text(string="Description")
    state = fields.Selection(
        selection=_STATES,
        string="Status",
        default="draft",
        required=True,
        tracking=True,
    )
    line_ids = fields.One2many(
        comodel_name="store.request.line",
        inverse_name="request_id",
        string="Store Request Lines",
        copy=True,
    )
    purchase_request_id = fields.Many2one(
        comodel_name="purchase.request",
        string="Linked Purchase Request",
        readonly=True,
    )
    operation_start_date = fields.Date(string="Operation Start Date", required=True)
    operation_end_date = fields.Date(string="Operation End Date", required=True)
    operation_type = fields.Selection(
        selection=[
            ('type1', 'Type 1'),
            ('type2', 'Type 2'),
            ('type3', 'Type 3')
        ],
        string="Operation Type",
        required=True
    )
    operation_name = fields.Char(string="Operation Name", required=True)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('store.request') or _('New')
        return super(StoreRequest, self).create(vals)

    def action_to_approve(self):
        self.write({"state": "to_approve"})

    def action_approve(self):
        self.write({"state": "approved"})
        self.create_purchase_request()

    def action_reject(self):
        self.write({"state": "rejected"})

    def create_purchase_request(self):
        if self.purchase_request_id:
            raise UserError(
                _("A purchase request has already been created for this store request.")
            )

        purchase_request_vals = {
            "requested_by": self.requested_by.id,
            "description": self.description,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": line.product_id.id,
                        "product_qty": line.product_qty,
                        "estimated_cost": line.estimated_cost,
                    },
                )
                for line in self.line_ids
            ],
        }
        purchase_request = self.env["purchase.request"].create(purchase_request_vals)
        self.purchase_request_id = purchase_request.id

class StoreRequestLine(models.Model):
    _name = "store.request.line"
    _description = "Store Request Line"

    request_id = fields.Many2one(
        comodel_name="store.request", string="Store Request", required=True
    )
    product_id = fields.Many2one(
        comodel_name="product.product", string="Product", required=True
    )
    product_qty = fields.Float(string="Quantity", required=True)
    estimated_cost = fields.Float(string="Estimated Cost")
    last_vendor_id = fields.Many2one(
        comodel_name="res.partner", string="Last Vendor", compute="_compute_last_vendor_and_price"
    )
    last_price = fields.Float(string="Last Price", compute="_compute_last_vendor_and_price")

    @api.depends('product_id')
    def _compute_last_vendor_and_price(self):
        for line in self:
            last_purchase_order_line = self.env['purchase.order.line'].search([
                ('product_id', '=', line.product_id.id)
            ], order='date_order desc', limit=1)
            if last_purchase_order_line:
                line.last_vendor_id = last_purchase_order_line.partner_id.id
                line.last_price = last_purchase_order_line.price_unit
            else:
                line.last_vendor_id = False
                line.last_price = 0.0