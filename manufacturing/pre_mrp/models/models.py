from odoo import fields,models,api,_
from datetime import datetime

from odoo.exceptions import ValidationError,UserError
class SalesOrder(models.Model):
    _inherit="sale.order"
    
    created_by = fields.Many2one('hr.employee',string="Created By")
    approved_by= fields.Many2one('hr.employee',string="Approved By")
    testing_service = fields.Boolean(string="Is Testing", default=False)
    @api.model
    def create(self, vals):
        if 'created_by' not in vals:
            vals['created_by'] = self.env.user.employee_id.id
        return super(SalesOrder, self).create(vals)
    
    def action_confirm(self):
        
        for line in self.order_line:
           

                self.env['mrp.planing'].create(
                    {
                        'product': line.product_id.id,
                        'expiration_date': self.validity_date,
                        'quantity': line.product_uom_qty,
                        'description': line.name,
                        'status': 'confirmed',
                        'sales_order': self.id,
                    }
                )
                # self.env['quality.test.plan'].create({
                #     'sales_order_id': self.id,
                #     'product_id': line.product_id.id,
                # })
            
                if not self.env.user.has_group('pre_mrp.group_sales_order_manager'):
                    raise ValidationError(_("You do not have the necessary permissions to confirm this order. Please contact your manager."))

        

        return super().action_confirm()

class MrpPlaning(models.Model):
    _name="mrp.planing"
    _description="Mrp Planning"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Reference", readonly=True, required=False, copy=False, default="New")
    product= fields.Many2one('product.product',string="Product")
    sales_order= fields.Many2one('sale.order',string="Sales Order")
    expiration_date= fields.Datetime(string="Dead Line")
    quantity= fields.Float(string="Quantity")
    description= fields.Text(string="Description")
    scheduled_date= fields.Datetime(string="Scheduled Date",tracking=True)
    approval_date = fields.Date(string="Approval Date", default= datetime.today() )
    approved_by = fields.Many2one('hr.employee',string="Approved By", default = lambda self: self.env.user.employee_id)
    status = fields.Selection([(i,i.upper()) for i in ['draft','confirmed','approved','received']], default="draft",tracking=True)
    template=fields.Many2one('mrp.plan.template', string="Template")
    od_min= fields.Float(string="OD min", compute="_get_attrs",default=0.0, store=True) 
    od_max = fields.Float(string="OD max", compute="_get_attrs",default=0.0, store=True)
    t_min = fields.Float(string="T min", compute="_get_attrs",default=0.0, store=True) 
    t_max = fields.Float(string="T max", compute="_get_attrs",default=0.0, store=True)
    sdr = fields.Float(string="SDR", compute="_get_attrs",default=0.0, store=True)
    pn = fields.Float(string="PN", compute="_get_attrs",default=0.0, store=True) 
    average_kg_per_m = fields.Float(string="Average kg/m", compute="_average_weight_per_meter",store=True)
    meter = fields.Float(string="Meter", compute="_get_attrs",default=0.0,store=True) 
    kg = fields.Float(string="Weight", compute="_get_attrs",default=0.0,store=True) 
    estimated_scrap_kg = fields.Float(string="Estimated Scrap KG (4.5%)", compute="_compute_scrap_kg",store=True) 
    total_rm_used = fields.Float(string="Total RM Used", compute="_get_attrs",default=0.0,store=True) 
    requested_rm_in_bag = fields.Float(string="Requested RM in bag", compute="_get_attrs",default=0.0,store=True)
    required_coil_length= fields.Float(string="Required Coil Length (M)", compute="_get_attrs",default=0.0,store=True)
    received_by = fields.Many2one('hr.employee',string="Received By")
    created_by= fields.Many2one('hr.employee', string="Created By", default = lambda self: self.env.user.employee_id.id)
    created_date=fields.Date(string="Date", default=datetime.today())
    @api.depends('template')
    def _get_attrs(self):
        for rec in self:
            if rec.template:
                rec.od_max= rec.template.od_max
                rec.od_min = rec.template.od_min
                rec.t_max= rec.template.t_max
                rec.t_min= rec.template.t_min
                rec.sdr= rec.template.sdr
                rec.pn= rec.template.pn
                rec.meter= rec.template.meter
                rec.kg= rec.template.kg
                rec.total_rm_used = rec.template.total_rm_used
                rec.requested_rm_in_bag= rec.template.requested_rm_in_bag
                rec.required_coil_length= rec.template.required_coil_length
    @api.depends('meter','kg')
    def _average_weight_per_meter(self):
        for rec in self:
            if rec.meter and rec.kg:
                rec.average_kg_per_m = round((rec.kg / rec.meter),2)
            else:
                rec.average_kg_per_m = 0.0
                
    @api.depends('kg')
    def _compute_scrap_kg(self):
        for rec in self:
            if rec.kg:
                rec.estimated_scrap_kg = round((rec.kg * 0.045),2)
            else:
                rec.estimated_scrap_kg = 0.0
                
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('mrp.planing') or 'New'
        
        return super(MrpPlaning, self).create(vals)
    def approve(self):
        
        
        self.status="approved"
        self.approved_by = self.env.user.employee_id.id
        bom = self.env['mrp.bom'].search([
            ('product_tmpl_id', '=', self.product.product_tmpl_id.id)
        ], limit=1)

        # if not bom:
        #     raise ValidationError("No Bill of Materials (BOM) found for the selected product.")

        # Prepare raw material moves from BOM lines
        move_raw_ids = [
            (0, 0, {
                'product_id': line.product_id.id,
                'product_uom_qty': line.product_qty * self.quantity / bom.product_qty,  # Scale by production quantity
                'product_uom': line.product_uom_id.id,
                'name': line.product_id.display_name,
                'location_id': self.env['stock.location'].search([('usage', '=', 'internal')], limit=1).id,
                'location_dest_id': self.env['stock.location'].search([('usage', '=', 'production')], limit=1).id,
            })
            for line in bom.bom_line_ids
        ]

        production= self.env['mrp.production'].create({
            'product_id': self.product.id,
            'product_uom_id': self.product.uom_id.id,
            'product_qty': self.quantity,
            'date_planned_start': self.scheduled_date,
            'bom_id': bom.id ,
            'move_raw_ids': move_raw_ids,
            'state': 'draft',
            "mrp_plan": self.id
        })
        qa_test = self.env['quality.test.plan'].search([

('sales_order_id','=',self.sales_order.id),
('product_id','=',self.product.id)
        ]
                        
                    )
        qa_test.production_id= production.id

    def received(self):
        for rec in self:
            self.received_by = self.env.user.employee_id.id
            self.status = 'received'
    
    def confirm(self):
        self.status="confirmed"
        self.created_by = self.env.user.employee_id.id
    
    def reset_to_draft(self):
        self.status="draft"
    
class MrpPlanTemplate(models.Model):
    _name="mrp.plan.template"
    _description = 'Mrp Planning template for the fields'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name=fields.Char(string="Name")
    od_min= fields.Float(string="OD min") 
    od_max = fields.Float(string="OD max")
    t_min = fields.Float(string="T min") 
    t_max = fields.Float(string="T max")
    sdr = fields.Float(string="SDR")
    pn = fields.Float(string="PN") 
    average_kg_per_m = fields.Float(string="Average kg/m", compute="_average_weight_per_meter",store=True)
    meter = fields.Float(string="Meter") 
    kg = fields.Float(string="Weight") 
    estimated_scrap_kg = fields.Float(string="Estimated Scrap KG (4.5%)", compute="_compute_scrap_kg",store=True) 
    total_rm_used = fields.Float(string="Total RM Used") 
    requested_rm_in_bag = fields.Float(string="Requested RM in bag")
    required_coil_length= fields.Float(string="Required Coil Length (M)")
    
    
    @api.depends('meter','kg')
    def _average_weight_per_meter(self):
        for rec in self:
            if rec.meter and rec.kg:
                rec.average_kg_per_m = round((rec.kg / rec.meter),2)
            else:
                rec.average_kg_per_m = 0.0
                
    @api.depends('kg')
    def _compute_scrap_kg(self):
        for rec in self:
            if rec.kg:
                rec.estimated_scrap_kg = round((rec.kg * 0.045),2)
            else:
                rec.estimated_scrap_kg = 0.0