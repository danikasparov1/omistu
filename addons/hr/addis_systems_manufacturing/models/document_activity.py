from odoo import api,_, fields, models
from odoo.exceptions import ValidationError,UserError
class MrpProductionInherited(models.Model):
    _inherit="mrp.production"
    activity_state=fields.Selection([
        ("edited","edited"),
    ],compute="_document_activity_state",string="State",store=True
    )

    @api.depends('create_date', 'write_date')
    def _document_activity_state(self):
        for record in self:
            if record.create_date != record.write_date:
                record.activity_state="edited"
        return []