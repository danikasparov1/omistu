# from odoo import models, fields, api
# from odoo.exceptions import ValidationError
# import re

# class ResPartner(models.Model):
#     _inherit = 'res.partner'
    
#     fan_number = fields.Char(
#         string='FAN Number (16-digit)',
#         size=16,
#         help='16-digit national identification number'
#     )
    
#     fin_number = fields.Char(
#         string='FIN Number (8-digit)',
#         size=8,
#         help='8-digit national identification number'
#     )
    
#     @api.constrains('fan_number')
#     def _check_fan_number(self):
#         for record in self:
#             if record.fan_number and not re.match(r'^\d{16}$', record.fan_number):
#                 raise ValidationError('FAN Number must be exactly 16 digits')
    
#     @api.constrains('fin_number')
#     def _check_fin_number(self):
#         for record in self:
#             if record.fin_number and not re.match(r'^\d{8}$', record.fin_number):
#                 raise ValidationError('FIN Number must be exactly 8 digits')


# class ResUsers(models.Model):
#     _inherit = 'res.users'
    
#     fan_number = fields.Char(
#         string='FAN Number (16-digit)',
#         size=16,
#         help='16-digit national identification number'
#     )
    
#     fin_number = fields.Char(
#         string='FIN Number (8-digit)',
#         size=8,
#         help='8-digit national identification number'
#     )
    
#     @api.constrains('fan_number')
#     def _check_fan_number(self):
#         for record in self:
#             if record.fan_number and not re.match(r'^\d{16}$', record.fan_number):
#                 raise ValidationError('FAN Number must be exactly 16 digits')
    
#     @api.constrains('fin_number')
#     def _check_fin_number(self):
#         for record in self:
#             if record.fin_number and not re.match(r'^\d{8}$', record.fin_number):
#                 raise ValidationError('FIN Number must be exactly 8 digits')


# class HrEmployee(models.Model):
#     _inherit = 'hr.employee'
    
#     fan_number = fields.Char(
#         string='FAN Number (16-digit)',
#         size=16,
#         help='16-digit national identification number'
#     )
    
#     fin_number = fields.Char(
#         string='FIN Number (8-digit)',
#         size=8,
#         help='8-digit national identification number'
#     )
    
#     @api.constrains('fan_number')
#     def _check_fan_number(self):
#         for record in self:
#             if record.fan_number and not re.match(r'^\d{16}$', record.fan_number):
#                 raise ValidationError('FAN Number must be exactly 16 digits')
    
#     @api.constrains('fin_number')
#     def _check_fin_number(self):
#         for record in self:
#             if record.fin_number and not re.match(r'^\d{8}$', record.fin_number):
#                 raise ValidationError('FIN Number must be exactly 8 digits')


from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    fan_number = fields.Char(
        string='FAN Number (16-digit)',
        size=16,
        required=True,  # Make the field mandatory
        help='16-digit national identification number'
    )
    
    fin_number = fields.Char(
        string='FIN Number (8-digit)',
        size=8,
        required=True,  # Make the field mandatory
        help='8-digit national identification number'
    )
    
    @api.constrains('fan_number', 'fin_number')
    def _check_unique_and_format(self):
        for record in self:
            # Check FAN Number format
            if record.fan_number and not re.match(r'^\d{16}$', record.fan_number):
                raise ValidationError('FAN Number must be exactly 16 digits.')
            # Check FIN Number format
            if record.fin_number and not re.match(r'^\d{8}$', record.fin_number):
                raise ValidationError('FIN Number must be exactly 8 digits.')
            # Ensure FAN and FIN numbers are unique
            if self.search_count([('fan_number', '=', record.fan_number)]) > 1:
                raise ValidationError('FAN Number must be unique.')
            if self.search_count([('fin_number', '=', record.fin_number)]) > 1:
                raise ValidationError('FIN Number must be unique.')


class ResUsers(models.Model):
    _inherit = 'res.users'
    
    fan_number = fields.Char(
        string='FAN Number (16-digit)',
        size=16,
        required=True,  # Make the field mandatory
        help='16-digit national identification number'
    )
    
    fin_number = fields.Char(
        string='FIN Number (8-digit)',
        size=8,
        required=True,  # Make the field mandatory
        help='8-digit national identification number'
    )
    
    @api.constrains('fan_number', 'fin_number')
    def _check_unique_and_format(self):
        for record in self:
            # Check FAN Number format
            if record.fan_number and not re.match(r'^\d{16}$', record.fan_number):
                raise ValidationError('FAN Number must be exactly 16 digits.')
            # Check FIN Number format
            if record.fin_number and not re.match(r'^\d{8}$', record.fin_number):
                raise ValidationError('FIN Number must be exactly 8 digits.')
            # Ensure FAN and FIN numbers are unique
            if self.search_count([('fan_number', '=', record.fan_number)]) > 1:
                raise ValidationError('FAN Number must be unique.')
            if self.search_count([('fin_number', '=', record.fin_number)]) > 1:
                raise ValidationError('FIN Number must be unique.')


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    fan_number = fields.Char(
        string='FAN Number (16-digit)',
        size=16,
        required=True,  # Make the field mandatory
        help='16-digit national identification number'
    )
    
    fin_number = fields.Char(
        string='FIN Number (8-digit)',
        size=8,
        required=True,  # Make the field mandatory
        help='8-digit national identification number'
    )
    
    @api.constrains('fan_number', 'fin_number')
    def _check_unique_and_format(self):
        for record in self:
            # Check FAN Number format
            if record.fan_number and not re.match(r'^\d{16}$', record.fan_number):
                raise ValidationError('FAN Number must be exactly 16 digits.')
            # Check FIN Number format
            if record.fin_number and not re.match(r'^\d{8}$', record.fin_number):
                raise ValidationError('FIN Number must be exactly 8 digits.')
            # Ensure FAN and FIN numbers are unique
            if self.search_count([('fan_number', '=', record.fan_number)]) > 1:
                raise ValidationError('FAN Number must be unique.')
            if self.search_count([('fin_number', '=', record.fin_number)]) > 1:
                raise ValidationError('FIN Number must be unique.')