from odoo import models, fields

class ReportMrpProductionComponents(models.AbstractModel):
    _name = 'report.mrp.report_mrp_production_components'
    _description = 'MRP Production Report Components'

    def _get_report_values(self, docids, data=None):
        docs = self.env['mrp.production'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'mrp.production',
            'docs': docs,
        }
