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
        comodel_name="ohpurchase.request",
        string="Linked Purchase Request",
        readonly=True,
    )

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


# from odoo import models, fields, api, _
# from odoo.exceptions import UserError

# class StoreRequest(models.Model):
#     _name = 'store.request'
#     _description = 'Store Request'

#     name = fields.Char(string='Request Reference', required=True, copy=False, readonly=True, default=lambda self: _('New'))
#     date_requested = fields.Date(string='Request Date', default=fields.Date.today)
#     state = fields.Selection([
#         ('draft', 'Draft'),
#         ('submit', 'Submitted'),
#         ('approve', 'Approved'),
#         ('reject', 'Rejected'),
#         ('on_request', 'On Request'),
#         ('on_siv', 'On SIV')
#     ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')
#     request_lines = fields.One2many('store.request.line', 'request_id', string='Request Lines')
#     purchase_request_id = fields.Many2one('purchase.request', string='Purchase Request')
#     requested_by = fields.Many2one('res.users', string='Requested By')
#     description = fields.Text(string='Description')

#     def action_to_approve(self):
#         self.state = 'submit'

#     def action_approve(self):
#         self.state = 'approve'

#     def action_reject(self):
#         self.state = 'reject'

#     def create_purchase_request(self):
#         if self.purchase_request_id:
#             raise UserError(
#                 _("A purchase request has already been created for this store request.")
#             )

#         purchase_request_vals = {
#             "requested_by": self.requested_by.id,
#             "description": self.description,
#             "line_ids": [
#                 (
#                     0,
#                     0,
#                     {
#                         "product_id": line.product_id.id,
#                         "product_qty": line.product_qty,
#                         "estimated_cost": line.estimated_cost,
#                     },
#                 )
#                 for line in self.request_lines
#             ],
#         }
#         purchase_request = self.env["purchase.request"].create(purchase_request_vals)
#         self.purchase_request_id = purchase_request.id

#     def create_issue_voucher(self):
#         StoreIssueVoucher = self.env['store.issue.voucher']
#         StoreIssueVoucherLine = self.env['store.issue.voucher.line']
#         for request in self:
#             if request.state == "approve":
#                 request.state = "on_siv"
#             else:
#                 continue




# class StoreRequestLine(models.Model):
#     _name = "store.request.line"
#     _description = "Store Request Line"

#     request_id = fields.Many2one(
#         comodel_name="store.request", string="Store Request", required=True
#     )
#     product_id = fields.Many2one(
#         comodel_name="product.product", string="Product", required=True
#     )
#     product_qty = fields.Float(string="Quantity", required=True)
#     estimated_cost = fields.Float(string="Estimated Cost")





