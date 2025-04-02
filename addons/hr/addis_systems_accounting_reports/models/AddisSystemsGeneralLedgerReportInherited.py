from odoo import api, models, _, fields
from odoo.exceptions import UserError

import time


class AddisSystemsGeneralLedgerReportInherited(models.TransientModel):
    _inherit = 'account.report.general.ledger'

    def _get_redirect_link(self, line_id):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        move_id = self.env['account.move.line'].browse(line_id).move_id
        return f"{base_url}/web#id={move_id.id}&view_type=form&model={move_id._name}"
class AddisSystemsPartnerLedger(models.AbstractModel):
    _inherit = 'report.accounting_pdf_reports.report_partnerledger'
    @api.model
    def _get_report_values(self, docids, data=None):
        # Call the parent method and pass the `data` argument correctly
        results = super()._get_report_values(docids, data=data)
        x=self.env[data.get('context').get("active_model")].browse(data.get('context').get("active_id"))
        results['data']["form"]["period_from"]=x.period_from
        results['data']["form"]["period_to"]=x.period_to
        # Return the results so the report can render properly
        return results
    

class AddisSystemsTax(models.AbstractModel):
    _inherit = 'report.accounting_pdf_reports.report_tax'
    @api.model
    def _get_report_values(self, docids, data=None):
        # Call the parent method and pass the `data` argument correctly
        results = super()._get_report_values(docids, data=data)
        x=self.env[data.get('context').get("active_model")].browse(data.get('context').get("active_id"))
        results['data']["period_from"]=x.period_from
        results['data']["period_to"]=x.period_to
        # Return the results so the report can render properly
        return results
    
    