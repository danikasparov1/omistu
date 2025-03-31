# -*- coding: utf-8 -*-
# from odoo import http


# class Quality(http.Controller):
#     @http.route('/quality/quality', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/quality/quality/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('quality.listing', {
#             'root': '/quality/quality',
#             'objects': http.request.env['quality.quality'].search([]),
#         })

#     @http.route('/quality/quality/objects/<model("quality.quality"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('quality.object', {
#             'object': obj
#         })
