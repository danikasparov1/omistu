# from odoo import models, fields, api

# class CarWeight(models.Model):
#     _name = 'car.weight'
#     _description = 'Car Weight Tracking'

#     name = fields.Char(string='Car Reference', required=True)
#     operation_type = fields.Selection(
#         [('entry', 'Entry'), ('exit', 'Exit')],
#         string='Operation Type',
#         required=True,
#         default='entry'
#     )
#     entry_weight = fields.Float(string='Entry Weight (kg)', required=True)
#     exit_weight = fields.Float(string='Exit Weight (kg)')
#     result_weight = fields.Float(string='Result Weight (kg)', compute='_compute_result_weight', store=True)
#     entry_time = fields.Datetime(string='Entry Time', default=fields.Datetime.now, required=True)
#     exit_time = fields.Datetime(string='Exit Time')

#     @api.depends('entry_weight', 'exit_weight', 'operation_type')
#     def _compute_result_weight(self):
#         for record in self:
#             if record.operation_type == 'entry':
#                 # Compute raw material amount
#                 record.result_weight = record.entry_weight - record.exit_weight if record.exit_weight else 0.0
#             elif record.operation_type == 'exit':
#                 # Compute product weight
#                 record.result_weight = record.exit_weight - record.entry_weight if record.exit_weight else 0.0


# class CarEntryWeight(models.Model):
#     _name = 'car.entry.weight'
#     _description = 'Car Entry Weight'

#     reference_name = fields.Char(string='Reference Name', required=True)
#     default_car_weight = fields.Float(string='Default Car Weight (Kg)', required=True)
#     current_car_weight = fields.Float(string='Current Weight (Kg)', required=True)
#     raw_material_amount = fields.Float(string='Raw Material Amount (Kg)', compute='_compute_raw_material_amount')
#     entry_time = fields.Datetime(string='Entry Time', default=fields.Datetime.now, required=True)

#     # Add Many2one to link to CarWeight
#     car_weight_id = fields.Many2one('car.weight', string='Car Weight', required=True)

#     @api.depends('default_car_weight', 'current_car_weight')
#     def _compute_raw_material_amount(self):
#         for record in self:
#             record.raw_material_amount = record.current_car_weight - record.default_car_weight


# class CarExitWeight(models.Model):
#     _name = 'car.exit.weight'
#     _description = 'Car Exit Weight'

#     reference_name = fields.Char(string='Reference Name', required=True)
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
    operation_type = fields.Selection(
        [('entry', 'Entry'), ('exit', 'Exit')],
        string='Operation Type',
        required=True,
        default='entry'
    )
    entry_weight = fields.Float(string='Entry Weight (kg)', required=True)
    exit_weight = fields.Float(string='Exit Weight (kg)', required=True)
    result_weight = fields.Float(string='Result Weight (kg)', compute='_compute_result_weight', store=True)
    entry_time = fields.Datetime(string='Entry Time', default=fields.Datetime.now, required=True)
    exit_time = fields.Datetime(string='Exit Time')
    linked_car_id = fields.Many2one('car.weight', string='Linked Car', help="Link to another car for product tracking")
    driver_name = fields.Char(string='Driver Name')  # New field for driver name
    plate_number = fields.Char(string='Plate Number')  # New field for plate number

    @api.depends('entry_weight', 'exit_weight', 'operation_type')
    def _compute_result_weight(self):
        for record in self:
            if record.operation_type == 'entry':
                # Compute raw material amount
                record.result_weight = record.exit_weight - record.entry_weight
            elif record.operation_type == 'exit':
                # Compute product weight
                record.result_weight = record.entry_weight - record.exit_weight

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('car.weight') or 'New'
        return super(CarWeight, self).create(vals)


class CarEntryWeight(models.Model):
    _name = 'car.entry.weight'
    _description = 'Car Entry Weight'

    reference_name = fields.Char(string='Reference Name', required=True)
    default_car_weight = fields.Float(string='Default Car Weight (Kg)', required=True)
    current_car_weight = fields.Float(string='Current Weight (Kg)', required=True)
    raw_material_amount = fields.Float(string='Raw Material Amount (Kg)', compute='_compute_raw_material_amount')
    entry_time = fields.Datetime(string='Entry Time', default=fields.Datetime.now, required=True)
    car_weight_id = fields.Many2one('car.weight', string='Car Weight', required=True)

    @api.depends('default_car_weight', 'current_car_weight')
    def _compute_raw_material_amount(self):
        for record in self:
            record.raw_material_amount = record.current_car_weight - record.default_car_weight


class CarExitWeight(models.Model):
    _name = 'car.exit.weight'
    _description = 'Car Exit Weight'

    reference_name = fields.Char(string='Reference Name', required=True)
    default_car_weight = fields.Float(string='Default Car Weight (Kg)', required=True)
    current_car_weight = fields.Float(string='Current Weight (Kg)', required=True)
    produced_amount = fields.Float(string='Produced Amount (Kg)', compute='_compute_amount_weight')
    entry_time = fields.Datetime(string='Entry Time', default=fields.Datetime.now, required=True)
    car_weight_id = fields.Many2one('car.weight', string='Car Weight', required=True)

    @api.depends('default_car_weight', 'current_car_weight')
    def _compute_amount_weight(self):
        for record in self:
            record.produced_amount = record.current_car_weight - record.default_car_weight