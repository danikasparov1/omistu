from odoo import models, fields

class Service(models.Model):
    _name = 'event.service'
    _description = 'Event Service'

    name = fields.Char(string="Service Name", required=True)
    description = fields.Text(string="Description")
