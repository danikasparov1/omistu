from odoo import fields, models,api
from odoo.exceptions import ValidationError
from datetime import datetime

class ProductTemplateInherited(models.Model):
    _inherit = 'product.template'
    addis_expiration_year = fields.Integer(string="Expiration Date",  help='Number of Years after the receipt of the products (from the vendor'
        ' or in stock after production) after which the goods may become dangerous'
        ' and must not be consumed. It will be computed on the lot/serial number.')

    @api.onchange("addis_expiration_year")
    def set_expiratin_dates(self):
        for record in self:
            if record.addis_expiration_year or record.addis_expiration_year==0:
                record.expiration_time= 365*record.addis_expiration_year//1
