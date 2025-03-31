# -*- coding: utf-8 -*-
# from odoo import http


# class MrpStaging(http.Controller):
#     @http.route('/mrp_staging/mrp_staging', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mrp_staging/mrp_staging/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('mrp_staging.listing', {
#             'root': '/mrp_staging/mrp_staging',
#             'objects': http.request.env['mrp_staging.mrp_staging'].search([]),
#         })

#     @http.route('/mrp_staging/mrp_staging/objects/<model("mrp_staging.mrp_staging"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mrp_staging.object', {
#             'object': obj
#         })
