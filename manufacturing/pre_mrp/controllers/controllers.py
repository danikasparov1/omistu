# -*- coding: utf-8 -*-
# from odoo import http


# class PreMrp(http.Controller):
#     @http.route('/pre_mrp/pre_mrp', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pre_mrp/pre_mrp/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('pre_mrp.listing', {
#             'root': '/pre_mrp/pre_mrp',
#             'objects': http.request.env['pre_mrp.pre_mrp'].search([]),
#         })

#     @http.route('/pre_mrp/pre_mrp/objects/<model("pre_mrp.pre_mrp"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pre_mrp.object', {
#             'object': obj
#         })
