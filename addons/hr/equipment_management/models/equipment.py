from odoo import models, fields, api

# class Equipment(models.Model):
#     _name = 'equipment.management.equipment'
#     _description = 'Equipment Management'

#     name = fields.Char('Equipment Name', required=True)
#     description = fields.Text('Description')
#     components = fields.One2many('equipment.management.component', 'equipment_id', string='Components')
#     status = fields.Selection([
#         ('working', 'Working'),
#         ('not_working', 'Not Working'),
#         ('under_maintenance', 'Under Maintenance')
#     ], default='working')

#     workcenter_id = fields.Many2one(
#         'mrp.workcenter', string="Work Center",
#         help="The work center this equipment is associated with."
#     )

#     @api.model
#     def create(self, vals):
#         equipment = super(Equipment, self).create(vals)
#         equipment.check_components()
#         return equipment

#     def check_components(self):
#         """Checks components for malfunctions and sends an email if not working."""
#         for component in self.components:
#             if not component.is_working:
#                 component.send_notification()

class EquipmentCategory(models.Model):
    _name = 'equipment.management.category'
    _description = 'Equipment Category'

    name = fields.Char('Category Name', required=True)
    description = fields.Text('Description')

from odoo import models, fields, api

class Equipment(models.Model):
    _name = 'equipment.management.equipment'
    _description = 'Equipment Management'

    name = fields.Char('Equipment Name', required=True)
    description = fields.Text('Description')
    item_code = fields.Char('Item Code', required=True, help="Unique code for the equipment.")
    category_id = fields.Many2one(
        'equipment.management.category',  # Reference to the category model
        string='Category',
        required=True,
        help="Select the category for this equipment."
    )
    components = fields.One2many('equipment.management.component', 'equipment_id', string='Components')
    status = fields.Selection([
        ('working', 'Working'),
        ('not_working', 'Not Working'),
        ('under_maintenance', 'Under Maintenance')
    ], default='working')

    workcenter_id = fields.Many2one(
        'mrp.workcenter', string="Work Center",
        help="The work center this equipment is associated with."
    )

    @api.model
    def create(self, vals):
        equipment = super(Equipment, self).create(vals)
        equipment.check_components()
        return equipment

    def check_components(self):
        """Checks components for malfunctions and sends an email if not working."""
        for component in self.components:
            if not component.is_working:
                component.send_notification()

from odoo import models, fields

class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    equipment_ids = fields.One2many(
        'equipment.management.equipment', 'workcenter_id', string="Equipment",
        help="List of equipment associated with this work center."
    )

from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_finished_product = fields.Boolean(
        string="Is Finished Product",
        help="Indicates whether this product is a finished product (manufactured)."
    )

# from odoo import models, fields, api

# class MrpBomLine(models.Model):
#     _inherit = 'mrp.bom.line'

#     product_id = fields.Many2one(
#         'product.product',
#         string='Component',
#         domain="[('is_finished_product', '=', False)]",  # Exclude finished products
#         required=True,
#         help="Select a product that is not marked as a finished product."
#     )


from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    product_id = fields.Many2one(
        'product.product',
        string='Component',
        domain="[('is_finished_product', '=', False)]",  # Exclude finished products
        required=True,
        help="Select a product that is not marked as a finished product."
    )

    @api.model
    def create(self, vals):
        """Validate that the product is not a finished product before creating the BOM line."""
        product = self.env['product.product'].browse(vals.get('product_id'))
        if product.is_finished_product:
            raise ValidationError(
                _("You cannot add a finished product (%s) as a BOM component.") % product.name
            )
        return super(MrpBomLine, self).create(vals)

    def write(self, vals):
        """Validate that the product is not a finished product before updating the BOM line."""
        if 'product_id' in vals:
            product = self.env['product.product'].browse(vals.get('product_id'))
            if product.is_finished_product:
                raise ValidationError(
                    _("You cannot add a finished product (%s) as a BOM component.") % product.name
                )
        return super(MrpBomLine, self).write(vals)

    @api.constrains('product_id')
    def _check_is_finished_product(self):
        """Ensure that the product is not a finished product."""
        for line in self:
            if line.product_id.is_finished_product:
                raise ValidationError(
                    _("You cannot add a finished product (%s) as a BOM component.") % line.product_id.name
                )


from odoo import models, fields

class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_finished_product = fields.Boolean(
        string="Is Finished Product",
        # related='product_tmpl_id.is_finished_product',
        store=True,
        help="Indicates whether this product is a finished product (manufactured)."
    )


from odoo import models, fields

class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    equipment_ids = fields.One2many(
        'equipment.management.equipment',
        'workcenter_id',
        string="Equipment",
        help="List of equipment associated with this workcenter."
    )