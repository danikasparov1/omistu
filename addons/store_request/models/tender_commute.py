# # from odoo import models, fields, api

# # class TenderValuationCommute(models.Model):
# #     _name = 'tender.valuation.commute'
# #     _description = 'Tender Valuation Commute'

# #     user_id = fields.Many2one('res.users', string='User', required=True)
# #     name = fields.Char(string='Name', readonly=True)
# #     title = fields.Char(string='Title', default='Tender Valuation Commute')

# #     score_ids = fields.One2many(
# #         'technical.valuation.scores',  # Related model
# #         'tender_id',  # Field in the related model that references this model
# #         string='Technical Valuation Scores'
# #     )

# #     # Computed field for total_score
# #     total_score = fields.Float(
# #         string='Total Score',
# #         compute='_compute_total_score',
# #         store=True  # Store the value in the database for faster access
# #     )

# #     @api.depends('score_ids.actual_score')
# #     def _compute_total_score(self):
# #         """
# #         Compute the total_score as the sum of actual_score from related technical.valuation.scores records.
# #         """
# #         for record in self:
# #             record.total_score = sum(record.score_ids.mapped('actual_score'))

# #     @api.model
# #     def create(self, vals):
# #         # Automatically derive the name from the user’s name
# #         user = self.env['res.users'].browse(vals.get('user_id'))
# #         vals['name'] = user.name if user else 'Unknown User'
# #         return super(TenderValuationCommute, self).create(vals)



# from odoo import models, fields, api

# class TenderValuationCommute(models.Model):
#     _name = 'tender.valuation.commute'
#     _description = 'Tender Valuation Commute'

#     # vendor_id = fields.Many2one('res.partner', string='Vendor', required=True, domain=[('supplier', '=', True)])
#     vendor_id = fields.Many2one('res.partner', string='Vendor', required=True, domain=[('supplier_rank', '>', 0)])

#     name = fields.Char(string='Name', readonly=True)
#     title = fields.Char(string='Title', default='Tender Valuation Commute')

#     # One2many field for technical valuation scores, assuming 'tender_id' is a foreign key in the related model
#     score_ids = fields.One2many(
#         'technical.valuation.scores',  # Related model
#         'tender_id',  # Field in the related model that references this model
#         string='Technical Valuation Scores'
#     )

#     # Computed field for total_score
#     total_score = fields.Float(
#         string='Total Score',
#         compute='_compute_total_score',
#         store=True  # Store the value in the database for faster access
#     )

#     @api.depends('score_ids.actual_score')
#     def _compute_total_score(self):
#         """
#         Compute the total_score as the sum of actual_score from related technical.valuation.scores records.
#         """
#         for record in self:
#             record.total_score = sum(record.score_ids.mapped('actual_score'))

#     @api.model
#     def create(self, vals):
#         # Automatically derive the name from the vendor’s name
#         vendor = self.env['res.partner'].browse(vals.get('vendor_id'))
#         vals['name'] = vendor.name if vendor else 'Unknown Vendor'
#         return super(TenderValuationCommute, self).create(vals)



from odoo import models, fields, api

class TenderValuationCommute(models.Model):
    _name = 'tender.valuation.commute'
    _description = 'Tender Valuation Commute'

    # Assuming you have a Many2one relation with purchase_tender model
    purchase_tender_id = fields.Many2one('purchase.tender', string='Purchase Tender', required=True)

    # # Updated domain to restrict to vendors from Purchase Tender Lines
    # vendor_id = fields.Many2one('res.partner', string='Vendor', required=True, 
    #     domain=lambda self: [('id', 'in', self._get_vendor_ids())])
    vendor_id = fields.Many2one('res.partner', string='Vendor', required=True)

    name = fields.Char(string='Name', readonly=True)
    title = fields.Char(string='Title', default='Tender Valuation Commute')

    score_ids = fields.One2many(
        'technical.valuation.scores',  # Related model
        'tender_id',  # Field in the related model that references this model
        string='Technical Valuation Scores'
    )

    total_score = fields.Float(
        string='Total Score',
        compute='_compute_total_score',
        store=True  # Store the value in the database for faster access
    )

    @api.depends('score_ids.actual_score')
    def _compute_total_score(self):
        """Compute the total_score as the sum of actual_score from related technical.valuation.scores records."""
        for record in self:
            record.total_score = sum(record.score_ids.mapped('actual_score'))

    @api.model
    def create(self, vals):
        # Automatically derive the name from the vendor’s name
        vendor = self.env['res.partner'].browse(vals.get('vendor_id'))
        vals['name'] = vendor.name if vendor else 'Unknown Vendor'
        return super(TenderValuationCommute, self).create(vals)

    def _get_vendor_ids(self):
        """
        Get vendor IDs from all purchase tender lines related to the current tender.
        """
        if self.purchase_tender_id:
            tender_lines = self.env['purchase.tender.line'].search([('purchase_tender_id', '=', self.purchase_tender_id.id)])
            return tender_lines.mapped('partner_id').ids
        return []


class TenderEvaluationCommittee(models.Model):
    _name = 'tender.evaluation.committee'
    _description = 'Tender Evaluation Committee'

    name = fields.Char(string='Committee Name', required=True)
    tender_id = fields.Many2one('purchase.tender', string='Purchase Tender', required=True)
    evaluation_ids = fields.One2many('vendor.evaluation.score', 'committee_id', string='Evaluations')


class VendorEvaluationScore(models.Model):
    _name = 'vendor.evaluation.score'
    _description = 'Vendor Evaluation Score'

    vendor_id = fields.Many2one('res.partner', string='Vendor', required=True)
    committee_id = fields.Many2one('res.users', string='Committee', required=True)
    score = fields.Float(string='Score')

    @api.model
    def create(self, vals):
        record = super(VendorEvaluationScore, self).create(vals)
        record._update_vendor_average()
        return record

    def write(self, vals):
        res = super(VendorEvaluationScore, self).write(vals)
        self._update_vendor_average()
        return res

    def _update_vendor_average(self):
        """Update average committee score in related tender lines"""
        for record in self:
            tender_lines = self.env['purchase.tender.line'].search([
                ('partner_id', '=', record.vendor_id.id)
            ])
            tender_lines._compute_average_committee_score()
