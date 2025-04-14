# # from odoo import models, fields, api

# # class CrmLead(models.Model):
# #     _inherit = 'crm.lead'

# #     property_ids = fields.Many2many('property.management', string='Properties')

# #     @api.model
# #     def create(self, values):
# #         lead = super(CrmLead, self).create(values)
# #         if lead.property_ids:
# #             for property in lead.property_ids:
# #                 property.sudo().write({
# #                     'quantity': property.quantity - 1  # Decrease the quantity of the property
# #                 })
# #         return lead


# from odoo import models, fields, api

# class CrmLead(models.Model):
#     _inherit = 'crm.lead'

#     property_ids = fields.Many2many('property.management', string='Selected Properties')

#     @api.model
#     def create(self, values):
#         lead = super(CrmLead, self).create(values)
#         for property in lead.property_ids:
#             if property.status == 'available':
#                 property.sudo().mark_as_sold()  # Mark property as sold when assigned
#         return lead



from odoo import models, fields, api

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    property_ids = fields.Many2many('property.management', string='Selected Properties')

    @api.model
    def create(self, values):
        lead = super(CrmLead, self).create(values)
        for property in lead.property_ids:
            if property.status == 'available' and property.quantity > 0:
                property.sudo().decrease_quantity()  # Reduce available quantity
        return lead
