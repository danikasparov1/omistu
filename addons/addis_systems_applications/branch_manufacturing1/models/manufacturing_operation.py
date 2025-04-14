from odoo import models, fields

class Branch(models.Model):
    _name = 'branch'
    _description = 'Branch'

    name = fields.Char(string='Branch Name', required=True)
    location = fields.Char(string='Location')
