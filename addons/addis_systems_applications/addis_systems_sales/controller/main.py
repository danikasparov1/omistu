from odoo import http
from odoo.http import request, content_disposition
from . import  samplefile as convert

class MyController(http.Controller):
    @http.route('/thirdparty/xml/<move_id>', type='http', auth='user')
    def download_file(self, move_id, **kwargs):
        move=request.env['account.move'].browse(int(move_id))
        pretty_xml_str_with_decl=convert.wrte_xml_file(move)
        filename = f'{move.name.replace("/","_")}.xml'
        response = request.make_response(
            pretty_xml_str_with_decl,
            headers=[
                ('Content-Type', 'application/xml'),
                ('Content-Disposition', f'attachment; filename={filename};')
            ]
        )
        move.is_xml_downloaded = True
        return response

