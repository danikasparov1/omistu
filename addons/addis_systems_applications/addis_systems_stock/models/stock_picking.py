from odoo import api,_, fields, models
from odoo.exceptions import ValidationError,UserError
import random
class StockPickingType(models.Model):
     _inherit="stock.picking.type"
     code = fields.Selection(selection_add=[('no_inventory_impact', 'No inventory impact')],ondelete={'no_inventory_impact': lambda recs: recs.write({'code': 'incoming', 'active': False})})
     count_crp_todo = fields.Integer(string="Number of Sent Orders", compute='_get_count_crp_todo')
     count_null=fields.Integer(default=17.0)
     klj=fields.Char(default="abd")
     def get_sent_requests(self):
        domain=[("state","=","sent"),("picking_type_id","=",self.id)]
        return self.env['customer.product.request'].search_count(domain)
     def _get_count_crp_todo(self):
        for record in self:
            if record.code=='no_inventory_impact':
                record.count_crp_todo=record.get_sent_requests()
            else:
                record.count_crp_todo=0
     def get_customer_request_stock_picking_action_picking_type(self):
        return {

        }

class CustomerProductRequestLine(models.Model):
     _name="customer.product.request.line"
     product_id = fields.Many2one(
        comodel_name='product.product',
        string="Product",
        change_default=True, ondelete='restrict', index='btree_not_null',
        domain="[('sale_ok', '=', True)]")
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
        comodel_name='customer.product.request',
        string="Order Reference",
        required=True, ondelete='cascade', index=True, copy=False)
     @api.depends('product_id')
     def _compute_product_template_id(self):
        for line in self:
            line.product_template_id = line.product_id.product_tmpl_id
class CustomerProductRequest(models.Model):
    _name = "customer.product.request"
    _description="Customer Requests"
    _order = 'requested_date desc, id desc'
    _rec_name = 'name'

    active = fields.Boolean('Active', default=True, help="By unchecking the active field, you may hide an Catalogue Request you will not use.")

    partner_id = fields.Many2one('res.partner', string='Requested by', required=False)
    user_id = fields.Many2one('res.users', string='Requested by')
    name = fields.Char(
        string="Order Reference",
        required=True, copy=False, readonly=False,
        default=lambda self: _('New'))
    state = fields.Selection([('draft', 'Draft'), ('sent', 'Sent'), (
        'validated', 'Validated'), ('canceled', 'Canceled')], required=True, default='draft')
    requested_date = fields.Datetime(string='Requested Date', required=True,copy=False,
                                 default=fields.Datetime.now)
    expire_date = fields.Date(string='Dead line', required=False)
    expired = fields.Boolean(string='Expired', compute="compute_catalogue_request_deadline")
    request_line = fields.One2many(
        comodel_name='customer.product.request.line',
        inverse_name='request_id',
        string="Order Lines",
        copy=True, auto_join=True)
    
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation Type',  readonly=False,
        domain="[('code', '=', 'no_inventory_impact')]",
        required=True, check_company=True, index=True)
    company_id = fields.Many2one(
        'res.company', 'Company', default=lambda self: self.env.company,
        index=True, required=True)
    

    
    def action_print(self):
        return self.env.ref('addis_systems_stock.action_report_customer_request').report_action(self)

    def action_confirm(self):
       for record in self:
           if not record.request_line:
               raise ValidationError("There must be at least one line to request")
           for line in record.request_line:
               if line.qty_requested <= 0:
                   raise ValidationError("Product Quantity Can not be zero or negative")   
           record.state="sent"
    def action_validate(self):
        for record in self:
            record.state="validated"
    def action_cancel(self):
        for record in self:
            record.state="canceled"
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _("New")) == _("New"):
                seq_date = fields.Datetime.context_timestamp(
                    self, fields.Datetime.to_datetime(vals['requested_date'])
                ) if 'requested_date' in vals else None
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'customer.product.request', sequence_date=seq_date) or _("New")
            pick_type=vals.get("picking_type_id",False)
            if pick_type:
                prefd=self.env['stock.picking.type'].browse(pick_type).sequence_code
                vals["name"]=vals["name"].replace("CPR",prefd)
                
        return super().create(vals_list)
    @api.ondelete(at_uninstall=False)
    def _unlink_only_draft(self):
        for records in self:
            if records.state !="draft":
                raise UserError(f"You can not delete {records.state} requests")

