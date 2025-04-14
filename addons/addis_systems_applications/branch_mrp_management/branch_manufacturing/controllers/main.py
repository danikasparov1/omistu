from odoo import http

class BranchManufacturingController(http.Controller):
    @http.route('/branch/manufacturing/orders', auth='user')
    def branch_manufacturing_orders(self):
        return http.request.render('branch_manufacturing.branch_orders_template')
