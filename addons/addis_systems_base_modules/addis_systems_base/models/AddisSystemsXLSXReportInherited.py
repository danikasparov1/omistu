from odoo import api, exceptions, fields, models
from odoo.tools.safe_eval import safe_eval, time

import logging

_logger = logging.getLogger(__name__)

class AddisSystemsXLSXReportActionInherited(models.Model):
    _inherit = "ir.actions.report"
    
    report_type = fields.Selection(selection_add=[("xlsx", "XLSX")], ondelete={"xlsx": "set default"})
