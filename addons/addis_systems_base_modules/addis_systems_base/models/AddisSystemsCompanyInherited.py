from odoo import fields, models, api, _

import re

import logging
_logger = logging.getLogger(__name__)


def simplified_and_clean_lower_string(string):
    return re.sub(r'\W+', '', string).lower()


class AddisSystemsBaseConfigurationResCompanyInherited(models.Model):
    _inherit = "res.company"

    def addis_systems_currency_updater_in_days(self):
        base_currency = self.env.company.currency_id.name
        to = "USD"
        for active_currency in self.env['res.currency'].search([('active', 'in', [False, True])]):
            if active_currency.name not in ['USD', base_currency]:
                to = f"{to},{active_currency.name}"
        string_ = f"https://api.fastforex.io/fetch-multi?from={base_currency}&to={to}&api_key=472be8568a-ef13f6dcf8-sjag0j"
        sample_response = {"base": "ETB",
                    "results": {"USD": 0.009, "EUR": 0.00814, "AED": 0.03303, "AFN": 0.63203, "ALL": 0.80933, "AMD": 3.4797, "ANG": 0.01607, "AOA": 8.26274, "ARS": 8.57397, "AUD": 0.01338, "AWG": 0.01628, "AZN": 0.01528, "BAM": 0.01591, "BBD": 0.01799, "BDT": 1.07922, "BGN": 0.01588, "BHD": 0.00338,
                                "BIF": 25.91664,
                                "BMD": 0.00899, "BND": 0.01174, "BOB": 0.06229, "BRL": 0.05077, "BSD": 0.00901, "BTN": 0.75425, "BWP": 0.12031, "BZD": 0.01812, "CAD": 0.01219, "CDF": 25.42714, "CHF": 0.00766, "CLF": 0.00022, "CLP": 8.42949, "CNH": 0.06402, "CNY": 0.06401, "COP": 37.69674,
                                "CUP": 0.21591,
                                "CVE": 0.89758, "CZK": 0.20411, "DJF": 1.60343, "DKK": 0.06071, "DOP": 0.53849, "DZD": 1.19871, "EGP": 0.4361, "ERN": 0.13615, "FJD": 0.01992, "FKP": 0.00685, "GBP": 0.00685, "GEL": 0.02417, "GHS": 0.14019, "GIP": 0.00685, "GMD": 0.5077, "GNF": 77.81045,
                                "GTQ": 0.06952, "GYD": 1.87934,
                                "HKD": 0.07016, "HNL": 0.22288, "HRK": 0.05802, "HTG": 1.2053, "HUF": 3.19954, "IDR": 139.03031, "ILS": 0.03335, "INR": 0.75492, "IQD": 11.76906, "IRR": 377.90298, "ISK": 1.25044, "JMD": 1.41753, "JOD": 0.00637, "JPY": 1.30475, "KES": 1.15394, "KGS": 0.75855,
                                "KHR": 36.6141,
                                "KMF": 4.01049, "KPW": 8.09701, "KRW": 12.04528, "KWD": 0.00275, "KYD": 0.00737, "KZT": 4.33857, "LAK": 198.91777, "LBP": 805.7052, "LKR": 2.68659, "LRD": 1.7568, "LSL": 0.16129, "LYD": 0.0429, "MAD": 0.08772, "MDL": 0.15638, "MGA": 40.99053, "MKD": 0.50161,
                                "MMK": 18.84799,
                                "MNT": 30.44845, "MOP": 0.07211, "MRU": 0.3584, "MUR": 0.41453, "MVR": 0.139, "MWK": 15.59965, "MXN": 0.1782, "MYR": 0.03916, "MZN": 0.57199, "NAD": 0.16068, "NGN": 14.34682, "NOK": 0.09604, "NPR": 1.20723, "NZD": 0.01452, "OMR": 0.00346, "PAB": 0.00899,
                                "PEN": 0.03405, "PGK": 0.0353,
                                "PHP": 0.50871, "PKR": 2.50687, "PLN": 0.03483, "PYG": 69.58643, "QAR": 0.03275, "RON": 0.04045, "RSD": 0.94802, "RUB": 0.80234, "RWF": 11.97454, "SAR": 0.03366, "SCR": 0.13362, "SDG": 5.38927, "SEK": 0.09278, "SGD": 0.01176, "SHP": 0.00685, "SLL": 202.66069,
                                "SOS": 5.14608,
                                "SRD": 0.25947, "SYP": 116.97646, "SZL": 0.16095, "THB": 0.30747, "TJS": 0.09594, "TMT": 0.03159, "TND": 0.02737, "TOP": 0.02087, "TRY": 0.30632, "TTD": 0.06101, "TWD": 0.28969, "TZS": 24.44675, "UAH": 0.37241, "UGX": 33.49337, "UYU": 0.36326, "UZS": 113.67493,
                                "VND": 223.53703,
                                "VUV": 1.05848, "WST": 0.02412, "XAF": 5.33771, "XCD": 0.02428, "XOF": 5.33771, "XPF": 0.97015, "YER": 2.24774, "ZAR": 0.16099, "ZMW": 0.2374}, "updated": "2024-09-04 13:21:16", "ms": 5}
        response_results = sample_response['results']
        for resp in response_results:
            if currency := self.env['res.currency'].search([('name', '=', str(resp)), ('active', 'in', [False, True])], limit=1):
                if not self.env['res.currency.rate'].search([('currency_id', '=', currency.id), ('name', '=', fields.Date.today())]):
                    currency_today_values = {"currency_id": currency.id, "name": fields.Date.today(), "company_rate": response_results[resp], "inverse_company_rate": response_results[resp]}
                    self.env['res.currency.rate'].sudo().create(currency_today_values)


# class AddisSystemsBaseConfigurationInherited(models.TransientModel):
#     _inherit = 'res.config.settings'



# class AddisSystemsResUsersInitMessageBoardInherited(models.Model):
#     _inherit = "res.users"


class ReportAction(models.Model):
    _inherit = "ir.actions.report"

    report_type = fields.Selection(selection_add=[("excel", "Excel")], ondelete={"excel": "set default"})



