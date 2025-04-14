from odoo import models, fields, api, exceptions

class QualityCheck(models.Model):
    _name = 'quality.check'
    _description = 'Quality Check'
    
    _inherit = 'mail.thread', 'mail.activity.mixin'
    
    
    name = fields.Char(string="Reference", readonly=True)
    user_id = fields.Many2one('res.users', readonly=True, string='Checked By',  default=lambda self: self.env.user)
    # product_id = fields.One2many('purchase.order.line', string='Products', required=True)
    stock_id = fields.Many2one('stock.picking', string='stock', readonly=True, required=True)
    move_ids = fields.One2many('stock.move', 'quality_check_id', related='stock_id.move_ids', readonly=True, store=True)
    
    # move_line_ids = fields.One2many('stock.move.line', 'picking_id', 'Operations')
    move_line_ids = fields.One2many('stock.move.line', 'quality_check_id', related='stock_id.move_line_ids', readonly=True, store=True)
    
    partner_id = fields.Many2one('res.partner', related='stock_id.partner_id', readonly=True, store=True)
    origin = fields.Char(related='stock_id.origin', string="Source Document")
    company_id = fields.Many2one('res.company', string='Company', readonly=True,
                                 default=lambda self: self.env.company,
                                 help='Company')
    
    inspection_date = fields.Datetime(string='Inspection Date',readonly=True, default=fields.Datetime.now)
    quality_state = fields.Selection([
        ('draft', 'Pending'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
    ], string='Inspection Result', default='draft', tracking=True, readonly=True, required=True)
    comments = fields.Text(string='Comments')
    additional_note = fields.Text(string='Note')
    
    
    
    @api.model
    def create(self, vals):
        """generate quality check sequence"""
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'quality.check') or 'New'
        result = super(QualityCheck, self).create(vals)
        return result

    
    def action_pass(self):
        self.write({
            'user_id': self.env.user,
            'quality_state': 'passed'
        })
            
    def action_fail(self):
        self.write({
            'user_id': self.env.user,
            'quality_state': 'failed'
        })
        
        
        self.stock_id.action_cancel()
        
        # Find and cancel the associated purchase.order
        
        purchase_order = self.env['purchase.order'].search([('name', '=', self.stock_id.origin)], limit=1)
        if purchase_order:
            purchase_order.button_cancel()
        # self.action_cancel()


