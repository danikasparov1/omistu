from odoo import http

class MyController(http.Controller):
    @http.route('/get_currency_symbol', type='json', auth='user')
    def get_currency_symbol(self):
        # Get the user's company currency
        user = http.request.env.user
        currency = user.company_id.currency_id
        return {'symbol': currency.symbol, 'position': currency.position}