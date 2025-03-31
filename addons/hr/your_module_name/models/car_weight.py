# from odoo import models, fields, api

# class CarWeight(models.Model):
#     _name = 'car.weight'
#     _description = 'Car Weight Tracking'

#     name = fields.Char(string='Car Reference', required=True)
#     entry_weight = fields.Float(string='Entry Weight (kg)', required=True)
#     exit_weight = fields.Float(string='Exit Weight (kg)')
#     product_weight = fields.Float(string='Loaded Product Weight (kg)', compute='_compute_product_weight', store=True)
#     entry_time = fields.Datetime(string='Entry Time', default=fields.Datetime.now, required=True)
#     exit_time = fields.Datetime(string='Exit Time')

#     @api.depends('entry_weight', 'exit_weight')
#     def _compute_product_weight(self):
#         for record in self:
#             if record.exit_weight:
#                 record.product_weight = record.exit_weight - record.entry_weight
#             else:
#                 record.product_weight = 0.0


# class CarExitWeight(models.Model):
#     _name = 'car.exit.weight'
#     _description = 'Car Exit Weight'

#     default_car_weight = fields.Float(string='Default Car Weight (Kg)', required=True)
#     current_car_weight = fields.Float(string='Current Weight (Kg)', required=True)
#     produced_amount = fields.Float(string='Produced Amount (Kg)', compute='_compute_amount_weight')
#     entry_time = fields.Datetime(string='Entry Time', default=fields.Datetime.now, required=True)

#     @api.depends('default_car_weight', 'current_car_weight')
#     def _compute_amount_weight(self):
#         for record in self:
#             record.produced_amount = record.current_car_weight - record.default_car_weight


# class CarEntryWeight(models.Model):
#     _name = 'car.entry.weight'
#     _description = 'Car Entry Weight'

#     default_car_weight = fields.Float(string='Default Car Weight (Kg)', required=True)
#     current_car_weight = fields.Float(string='Current Weight (Kg)', required=True)
#     produced_amount = fields.Float(string='Produced Amount (Kg)', compute='_compute_amount_weight')
#     entry_time = fields.Datetime(string='Entry Time', default=fields.Datetime.now, required=True)

#     # Add Many2one to link to CarWeight
#     car_weight_id = fields.Many2one('car.weight', string='Car Weight', required=True)

#     @api.depends('default_car_weight', 'current_car_weight')
#     def _compute_amount_weight(self):
#         for record in self:
#             record.produced_amount = record.current_car_weight - record.default_car_weight


from odoo import models, fields, api

class CarWeight(models.Model):
    _name = 'car.weight'
    _description = 'Car Weight Tracking'

    name = fields.Char(string='Car Reference', required=True)
    entry_weight = fields.Float(string='Entry Weight (kg)', required=True)
    exit_weight = fields.Float(string='Exit Weight (kg)')
    product_weight = fields.Float(string='Loaded Product Weight (kg)', compute='_compute_product_weight', store=True)
    entry_time = fields.Datetime(string='Entry Time', default=fields.Datetime.now, required=True)
    exit_time = fields.Datetime(string='Exit Time')

    @api.depends('entry_weight', 'exit_weight')
    def _compute_product_weight(self):
        for record in self:
            if record.exit_weight:
                record.product_weight = record.exit_weight - record.entry_weight
            else:
                record.product_weight = 0.0


class CarExitWeight(models.Model):
    _name = 'car.exit.weight'
    _description = 'Car Exit Weight'

    reference_name = fields.Char(string='Reference Name', required=True)
    default_car_weight = fields.Float(string='Default Car Weight (Kg)', required=True)
    current_car_weight = fields.Float(string='Current Weight (Kg)', required=True)
    produced_amount = fields.Float(string='Produced Amount (Kg)', compute='_compute_amount_weight')
    entry_time = fields.Datetime(string='Entry Time', default=fields.Datetime.now, required=True)

    @api.depends('default_car_weight', 'current_car_weight')
    def _compute_amount_weight(self):
        for record in self:
            record.produced_amount = record.current_car_weight - record.default_car_weight


class CarEntryWeight(models.Model):
    _name = 'car.entry.weight'
    _description = 'Car Entry Weight'

    reference_name = fields.Char(string='Reference Name', required=True)
    default_car_weight = fields.Float(string='Default Car Weight (Kg)', required=True)
    current_car_weight = fields.Float(string='Current Weight (Kg)', required=True)
    raw_material_amount = fields.Float(string='Raw Material Amount (Kg)', compute='_compute_raw_material_amount')
    entry_time = fields.Datetime(string='Entry Time', default=fields.Datetime.now, required=True)

    # Add Many2one to link to CarWeight
    car_weight_id = fields.Many2one('car.weight', string='Car Weight', required=True)

    @api.depends('default_car_weight', 'current_car_weight')
    def _compute_raw_material_amount(self):
        for record in self:
            record.raw_material_amount = record.current_car_weight - record.default_car_weight
