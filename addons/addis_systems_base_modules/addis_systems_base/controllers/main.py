from odoo import http
from odoo.http import content_disposition, request, route, serialize_exception as _serialize_exception
from odoo.tools import html_escape
from odoo.tools.safe_eval import safe_eval, time
from odoo.addons.web.controllers.report import ReportController

import string
import time
import secrets
import json
import logging

_logger = logging.getLogger(__name__)


def generate_token(length=32):
    characters = string.ascii_letters + string.digits
    token = ''.join(secrets.choice(characters) for _ in range(length))
    return token


class XLSXReportController(http.Controller):
    @http.route('/report/excel/', type='http', auth='user', methods=['POST'], csrf=False)
    def get_report_xlsx(self, model, options, output_format, report_name, **kw):
        uid = request.session.uid
        report_obj = request.env[model].with_user(uid)
        options = json.loads(options)
        token = generate_token()
        try:
            if output_format == 'xlsx':
                aa = report_obj.get_xlsx_report(options)

                response = request.make_response(
                    None, headers=[
                        ('Content-Type', 'application/vnd.ms-excel'),
                        ('Content-Disposition',
                         content_disposition(f"{report_name}.xlsx"))
                    ])
                response.set_cookie('fileToken', token)
                response.stream.write(aa)
                return response
        except Exception as e:
            se = http.serialize_exception(e)
            error = {
                'code': 200,
                'message': 'Odoo Server Error',
                'data': se
            }
            return request.make_response(html_escape(json.dumps(error)))