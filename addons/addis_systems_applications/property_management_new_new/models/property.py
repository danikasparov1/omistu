# # from odoo import models, fields

# # class Property(models.Model):
# #     _name = 'property.management'
# #     _description = 'Property Management'

# #     name = fields.Char(string='Property Name', required=True)
# #     location = fields.Char(string='Location')
# #     bedroom_count = fields.Selection(
# #         [('1', '1 Bedroom'), ('2', '2 Bedrooms'), ('3', '3 Bedrooms')],
# #         string='Bedroom Count', required=True)
# #     site = fields.Selection([('site_1', 'Site 1'), ('site_2', 'Site 2'), ('site_3', 'Site 3')],
# #                             string='Site', required=True)
# #     price = fields.Float(string='Price')
# #     quantity = fields.Integer(string='Quantity', default=1)


# from odoo import models, fields, api
# from odoo.exceptions import ValidationError

# class Property(models.Model):
#     _name = 'property.management'
#     _description = 'Property Management'
#     _inherit = ['mail.thread', 'mail.activity.mixin']  # Enables logging and notifications

#     name = fields.Char(string='Property Name', required=True, tracking=True)
#     site = fields.Selection([
#         ('bole_adeyabeba', 'Bole Adeyabeba'),
#         ('site_2', 'Site 2'),
#         ('site_3', 'Site 3')
#     ], string='Site', required=True, tracking=True)
#     floor = fields.Integer(string='Floor', required=True, tracking=True)
#     area = fields.Float(string='Area (m²)', required=True)
#     bedroom_count = fields.Selection([
#         ('1', 'One Bedroom'),
#         ('2', 'Two Bedrooms'),
#         ('3', 'Three Bedrooms')
#     ], string='Bedroom Count', required=True, tracking=True)
#     price = fields.Float(string='Price', default=0.0, tracking=True)
#     status = fields.Selection([
#         ('available', 'Available'),
#         ('sold', 'Sold')
#     ], string='Status', default='available', tracking=True)
#     property_code = fields.Char(string='Property Code', compute='_compute_property_code', store=True)

#     @api.depends('site', 'floor', 'area')
#     def _compute_property_code(self):
#         """Generates a unique property code based on the site, floor, and area."""
#         for record in self:
#             site_prefix = 'BA' if record.site == 'bole_adeyabeba' else 'S2' if record.site == 'site_2' else 'S3'
#             record.property_code = f"{site_prefix}-F{record.floor}-{int(record.area)}m²"

#     @api.constrains('price')
#     def _check_price(self):
#         for record in self:
#             if record.price < 0:
#                 raise ValidationError("Price cannot be negative.")

#     def mark_as_sold(self):
#         """Marks the property as sold."""
#         for record in self:
#             record.status = 'sold'


from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Property(models.Model):
    _name = 'property.management'
    _description = 'Property Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Enables logging and notifications

    name = fields.Char(string='Property Name', required=True, tracking=True)
    site = fields.Selection([
        ('bole_adeyabeba', 'Bole Adeyabeba'),
        ('site_2', 'Site 2'),
        ('site_3', 'Site 3')
    ], string='Site', required=True, tracking=True)
    floor = fields.Integer(string='Floor', required=True, tracking=True)
    area = fields.Float(string='Area (m²)', required=True)
    bedroom_count = fields.Selection([
        ('1', 'One Bedroom'),
        ('2', 'Two Bedrooms'),
        ('3', 'Three Bedrooms')
    ], string='Bedroom Count', required=True, tracking=True)
    price = fields.Float(string='Price', default=0.0, tracking=True)
    quantity = fields.Integer(string='Available Units', default=1, tracking=True)
    status = fields.Selection([
        ('available', 'Available'),
        ('sold', 'Sold')
    ], string='Status', default='available', tracking=True)
    property_code = fields.Char(string='Property Code', compute='_compute_property_code', store=True)

    @api.depends('site', 'floor', 'area')
    def _compute_property_code(self):
        """Generates a unique property code based on the site, floor, and area."""
        for record in self:
            site_prefix = 'BA' if record.site == 'bole_adeyabeba' else 'S2' if record.site == 'site_2' else 'S3'
            record.property_code = f"{site_prefix}-F{record.floor}-{int(record.area)}m²"

    @api.constrains('price', 'quantity')
    def _check_values(self):
        for record in self:
            if record.price < 0:
                raise ValidationError("Price cannot be negative.")
            if record.quantity < 0:
                raise ValidationError("Quantity cannot be negative.")

    def decrease_quantity(self):
        """Decreases property quantity by 1. If quantity reaches 0, marks property as sold."""
        for record in self:
            if record.quantity > 0:
                record.sudo().write({'quantity': record.quantity - 1})
                if record.quantity - 1 == 0:
                    record.sudo().write({'status': 'sold'})

    def mark_as_sold(self):
        """Marks property as sold when quantity reaches 0."""
        for record in self:
            record.status = 'sold'
