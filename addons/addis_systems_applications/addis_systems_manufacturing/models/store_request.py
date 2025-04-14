from odoo import api,_, fields, models
from odoo.exceptions import ValidationError,UserError,AccessError
import random



class StockPickingType(models.Model):
     _inherit="stock.picking.type"
     code = fields.Selection(
        selection_add=[('product_request', 'Product Request')],
        ondelete={
            'product_request': lambda recs: recs.write({'code': False, 'active': False})
        }
        )
     count_pr_todo = fields.Integer(string="Number of Sent Orders", compute='_get_count_pr_todo')
     count_pr_null=fields.Integer(default=0)

     def get_pr_sent_requests(self):
        domain=[("state","=","sent"),("picking_type_id","=",self.id)]
        return self.env['addisystems.product.request'].search_count(domain)
     
     def _get_count_pr_todo(self):
        for record in self:
            if record.code=='product_request':
                record.count_pr_todo=record.get_pr_sent_requests()
            else:
                record.count_pr_todo=0

            
     def get_product_request_stock_picking_action_picking_type(self):
        action = self.env.ref('addis_systems_manufacturing.open_stock_requests')
        return action.read()[0]
     
class ProductRequest(models.Model):
    _name = "addisystems.product.request"
    _description="Product Requests"
    _order = 'requested_date desc, id desc'
    _rec_name = 'name'

    manufacturing_order = fields.Many2one(
        comodel_name='mrp.production',  # Reference to the 'mrp.production' model
        string='Manufacturing Order',      # Label for the field
        required=False,                 # Whether the field is required
        ondelete='set null',            # Behavior when the related record is deleted
        help='Select the related production order.',  # Help text for the field
    )
    active = fields.Boolean('Active', default=True, help="By unchecking the active field, you may hide an Catalogue Request you will not use.")
    partner_id = fields.Many2one('res.partner', string='Requested by', required=False)
    user_id = fields.Many2one('res.users', string='Requested by')
    manager_id = fields.Many2one(
        'res.users',
        string='Manager',
        domain=lambda self: [('groups_id', 'in', [self.env.ref('addis_systems_manufacturing.group_manager_addis_stock_request').id])]
    )
    name = fields.Char(
        string="Order Reference",
        required=True, copy=False, readonly=False,
        default=lambda self: _('New'))
    state = fields.Selection([('draft', 'Draft'), ('sent', 'Sent'), (
        'validated', 'Validated'), ('canceled', 'Canceled')], required=True, default='draft')
    requested_date = fields.Datetime(string='Requested Date', required=True,copy=False,
                                 default=fields.Datetime.now)
    expire_date = fields.Date(string='Dead line', required=False)
    expired = fields.Boolean(string='Expired', compute="compute_product_request_deadline")
    request_line = fields.One2many(
        comodel_name='addisystems.product.request.line',
        inverse_name='request_id',
        string="Order Lines",
        copy=True, auto_join=True)
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation Type',  readonly=False,
        domain="[('code', '=', 'product_request')]",
        required=True, check_company=True, index=True ,default=lambda self : self.env['stock.picking.type'].search([('code','=','product_request')],limit=1).id )
    company_id = fields.Many2one(
        'res.company', 'Company', default=lambda self: self.env.company,
        index=True, required=True)
    
    can_approve = fields.Boolean(string='Can Approve', compute='_compute_can_approve')

    @api.depends_context('uid')
    def _compute_can_approve(self):
        is_approver = self.user_has_groups('addis_systems_manufacturing.group_manager_addis_stock_request')
        for record in self:
            if record.manager_id:
                is_approver=self.env.uid == record.manager_id.id
            record.can_approve = is_approver

            
    def action_print(self):
        return self.env.ref('addis_systems_stock.action_report_customer_request').report_action(self)

    from odoo.exceptions import ValidationError

    def action_confirm(self):
        for record in self:
        # Validation: Ensure quantities and request lines are correct
            for line in record.request_line:
                if line.qty_requested <= 0:
                    raise ValidationError("Product Quantity cannot be zero or negative.")
            
            if not record.request_line:
                raise ValidationError("There must be at least one line to request.")
            
            # Check manufacturing order and process stock moves

        record.state="sent"
    def action_validate(self):
        for record in self:
            if not record.can_approve:
                raise AccessError("You hAVE NO ACCESS TO VALIDATE STORE REQUESTS")
            else:
                if record.manufacturing_order:
                    for line in record.request_line:
                        stock_move = self.env['stock.move'].search(
                            [
                                ('product_id', '=', line.product_id.id),
                                ('raw_material_production_id', '=', record.manufacturing_order.id)
                            ],
                            limit=1
                        )
                        if stock_move:
                            # Update the quantity if stock move exists
                            stock_move.product_uom_qty += line.qty_requested
                        else:
                            # Create a new stock move if it doesn't exist
                            self.env['stock.move'].create({
                                'product_id': line.product_id.id,
                                'product_uom_qty': line.qty_requested,
                                'product_uom': line.product_id.uom_id.id,
                                'name': line.product_id.name,
                                'raw_material_production_id': record.manufacturing_order.id,
                            })
            record.state="validated"
    def action_cancel(self):
        for record in self:
            record.state="canceled"
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _("New")) == _("New"):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'addissystems.product.request.name')
        return super().create(vals_list)
    @api.ondelete(at_uninstall=False)
    def _unlink_only_draft(self):
        for records in self:
            if records.state !="draft":
                raise UserError(f"You can not delete {records.state} requests")
            


class ProductRequestLine(models.Model):
     _name="addisystems.product.request.line"
     product_id = fields.Many2one(
        comodel_name='product.product',
        string="Product",
        change_default=True, ondelete='restrict', index='btree_not_null',
        )
     product_template_id = fields.Many2one(
        string="Product Template",
        comodel_name='product.template',
        compute='_compute_product_template_id',
        readonly=False,
        search='_search_product_template_id',
        # previously related='product_id.product_tmpl_id'
        # not anymore since the field must be considered editable for product configurator logic
        # without modifying the related product_id when updated.
        domain=[('sale_ok', '=', True)])
     qty_requested = fields.Float(
        string="Quantity",
        digits='Product Unit of Measure')
     request_id = fields.Many2one(
        comodel_name='addisystems.product.request',
        string="Order Reference",
        required=True, ondelete='cascade', index=True, copy=False)
     @api.depends('product_id')
     def _compute_product_template_id(self):
        for line in self:
            line.product_template_id = line.product_id.product_tmpl_id