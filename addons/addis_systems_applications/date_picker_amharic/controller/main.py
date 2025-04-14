from odoo import http
from ethiopian_date import EthiopianDateConverter
import datetime

class DateController(http.Controller):    
    @http.route('/get_date_gregorian', type='json', auth='user')
    def get_date_to_gregorian(self,**kwargs):
        if not kwargs.get('date'):
            return ""
        date_to_be_converted=[int(i) for i in kwargs.get('date').split('/')][::-1]
        re_date = EthiopianDateConverter.to_gregorian(date_to_be_converted[0],date_to_be_converted[2],date_to_be_converted[1]).strftime("%F"),
        re_date = re_date[0]
        dates=re_date.split("-")
        newdates=f"{dates[1]}/{dates[2]}/{dates[0]}"
        return {'date': newdates
}
    