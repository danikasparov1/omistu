

from odoo import models, fields, api


# class CarWeight(models.Model):
#     _name = 'car.weight'
#     _description = 'Car Weight Tracking'

#     name = fields.Char(string='Source Document', required=True)
#     operation_type = fields.Selection(
#         [('entry', 'Entry'), ('exit', 'Exit')],
#         string='Operation Type',
#         required=True,
#         default='entry'
#     )
#     entry_weight = fields.Float(string='Entry Weight (kg)', required=True)
#     exit_weight = fields.Float(string='Exit Weight (kg)', required=True)
#     result_weight = fields.Float(string='Result Weight (kg)', compute='_compute_result_weight', store=True)
#     entry_time = fields.Datetime(string='Entry Time', default=fields.Datetime.now, required=True)
#     exit_time = fields.Datetime(string='Exit Time')
#     linked_car_id = fields.Many2one(
#         'car.registration',
#         string='Linked Car',
#         help="Select a registered car",
#         ondelete='set null'  # Set to null when the linked car is deleted
#     )
#     driver_name = fields.Char(string='Driver Name')
#     plate_number = fields.Char(string='Plate Number')
#     supplier_name = fields.Char(string='Supplier Name')
#     memo_number = fields.Char(string='Memo Number')  # New field for memo number

#     @api.depends('entry_weight', 'exit_weight', 'operation_type')
#     def _compute_result_weight(self):
#         for record in self:
#             if record.operation_type == 'entry':
#                 record.result_weight = record.exit_weight - record.entry_weight
#             elif record.operation_type == 'exit':
#                 record.result_weight = record.entry_weight - record.exit_weight

#     @api.model
#     def create(self, vals):
#         if vals.get('name', 'New') == 'New':
#             vals['name'] = self.env['ir.sequence'].next_by_code('car.weight') or 'New'
#         return super(CarWeight, self).create(vals)


from odoo import models, fields, api

class CarWeight(models.Model):
    _name = 'car.weight'
    _description = 'Car Weight Tracking'

    source_document = fields.Char(string='Source Document', required=True)  # Renamed from 'name'
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
    linked_car_id = fields.Many2one(
        'car.registration',
        string='Linked Car',
        help="Select a registered car",
        ondelete='set null'  # Set to null when the linked car is deleted
    )
    # Related fields to automatically fetch data from the linked car
    car_name = fields.Char(related='linked_car_id.name', string='Car Name', readonly=True)
    # product_loaded = fields.Char(related='product.product', string='product Loaded', readonly=True)
    # product_loaded = fields.Many2one()
    product_loaded = fields.Many2one('product.product', string='Products')
    vender_name = fields.Many2one('res.partner', string='Vender Name')
    # plate_number = fields.Char(related='linked_car_id.plate_number', string='Plate Number', readonly=True)
    plate_number = fields.Char(string='Plate Number')
    car_type = fields.Char(related='linked_car_id.car_type', string='Car Type', readonly=True)
    # driver_name = fields.Char(related='linked_car_id.driver_name', string='Driver Name', readonly=True)
    driver_name = fields.Char(string='Driver Name')
    # supplier_name = fields.Char(related='linked_car_id.supplier_name', string='Supplier Name', readonly=True)
    supplier_name = fields.Char(string='Supplier Name')
    memo_number = fields.Char(string='Memo Number')  # New field for memo number

    @api.depends('entry_weight', 'exit_weight', 'operation_type')
    def _compute_result_weight(self):
        for record in self:
            if record.operation_type == 'entry':
                record.result_weight = record.exit_weight - record.entry_weight
            elif record.operation_type == 'exit':
                record.result_weight = record.entry_weight - record.exit_weight

    @api.model
    def create(self, vals):
        if vals.get('source_document', 'New') == 'New':
            vals['source_document'] = self.env['ir.sequence'].next_by_code('car.weight') or 'New'
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