from odoo import models, fields

class CarRegistration(models.Model):
    _name = 'car.registration'
    _description = 'Car Registration'

    name = fields.Char(string='Car Name', required=True)
    plate_number = fields.Char(string='Plate Number', required=True)
    car_type = fields.Char(string='Car Type', required=True)
    driver_name = fields.Char(string='Driver Name')
    supplier_name = fields.Char(string='Supplier Name')