# from odoo import models, fields, api

# class CrmLead(models.Model):
#     _inherit = 'crm.lead'

#     property_ids = fields.Many2many('property.management', string='Selected Properties')

#     @api.model
#     def create(self, values):
#         lead = super(CrmLead, self).create(values)
#         for property in lead.property_ids:
#             if property.status == 'available' and property.quantity > 0:
#                 property.sudo().decrease_quantity()  # Reduce available quantity
#         return lead

#     def write(self, values):
#         res = super(CrmLead, self).write(values)
#         if 'stage_id' in values:
#             won_stage = self.env.ref('crm.stage_lead4')  # Assuming 'crm.stage_lead4' is the won stage
#             for lead in self:
#                 if lead.stage_id == won_stage:
#                     for property in lead.property_ids:
#                         if property.status == 'available':
#                             property.sudo().write({'status': 'sold'})
#         return res


from odoo import models, fields, api

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    property_ids = fields.Many2many(
        'property.management', 
        string='Selected Properties',
        domain=[('status', '=', 'available')]  # Only show available properties
    )

    @api.model
    def create(self, values):
        lead = super(CrmLead, self).create(values)
        for property in lead.property_ids:
            if property.status == 'available' and property.quantity > 0:
                property.sudo().decrease_quantity()  # Reduce available quantity
        return lead

    def write(self, values):
        res = super(CrmLead, self).write(values)
        if 'stage_id' in values:
            won_stage = self.env.ref('crm.stage_lead4')  # Assuming 'crm.stage_lead4' is the won stage
            for lead in self:
                if lead.stage_id == won_stage:
                    for property in lead.property_ids:
                        if property.status == 'available':
                            property.sudo().write({'status': 'sold'})
        return res



        