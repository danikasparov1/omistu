from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
LOCKED_FIELD_STATES = {
    state: [('readonly', True)]
    for state in {'done', 'cancel'}
}

class g2bProviderInfo(models.Model):
    _name = "g2b.provider.info"
    _description = "g2b provider info"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    name = fields.Char(string="Name", required=True)
    id_type = fields.Many2one('g2b.id.type', string="Id type", required=True)
    beneficiary_id = fields.Char(string="Id", required=True)
    phone = fields.Char(string="Phone")
    birth_date = fields.Datetime(string="Date of Birth", required=True)
    product_line = fields.One2many(
        comodel_name='g2b.product.line',
        inverse_name='provider_id',
        string="Product List",
        states=LOCKED_FIELD_STATES,
        copy=True, auto_join=True)
    state = fields.Selection([
            ('registered', 'Registered'),
            ('confirmed', 'Confirmed'),
            ('canceled', 'Canceled')
        ], string='Status', default='registered', tracking=True)
    image = fields.Binary(string="Image")
    region = fields.Char(string="Region")
    zone = fields.Char(string="Zone")
    woreda = fields.Char(string="Woreda")
    kebele = fields.Char(string="Kebele")

    def confirm_state(self):
        for rec in self:
            rec.state = 'confirmed'
