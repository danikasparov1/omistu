from odoo import fields, models, api, _
import re

import logging
import requests
import base64

_logger = logging.getLogger(__name__)


def simplified_and_clean_lower_string(string):
    return re.sub(r'\W+', '', string).lower()


class AddisSystemsPartnerInherited(models.Model):
    _inherit = "res.partner"

    invoice_pulsar_status = fields.Boolean(string="Invoice Pulsar Configured", default=False, compute="addis_systems_invoice_pulsar_status", store=False)
    sales_pulsar_status = fields.Boolean(string="Sales Pulsar Configured", default=False, compute="addis_systems_sales_pulsar_status", store=False)
    stock_pulsar_status = fields.Boolean(string="Stock Pulsar Configured", default=False, compute="addis_systems_stock_pulsar_status", store=False)
    payment_pulsar_status = fields.Boolean(string="Payment Pulsar Configured", default=False, compute="addis_systems_payment_pulsar_status", store=False)

    @api.depends("name", "vat")
    def addis_systems_invoice_pulsar_status(self):
        for rec in self:
            if rec.name and rec.vat and rec.company_type == "company":
                customer_data = {"Customer_Name": f"{rec.name}", "Tin_Number": f"{rec.vat}", "PulsarAPIAddress": f"{self.env.ref('base.main_company').addis_systems_invoice_pubsub_api_address}",
                                 "Namespace": f"{simplified_and_clean_lower_string(rec.name)}_invoice_and_payment"}
                customer_status = requests.post(f"{self.env.ref('base.main_company').addis_systems_client_application_support_api}/AddisSystems/Base/Partner/PulsarStatus", json=customer_data)
                if customer_status and customer_status.status_code == 200 and customer_status.json():
                    rec.invoice_pulsar_status = True
                else:
                    rec.invoice_pulsar_status = False
            else:
                rec.invoice_pulsar_status = False

    @api.depends("name", "vat")
    def addis_systems_sales_pulsar_status(self):
        for rec in self:
            if rec.name and rec.vat and rec.company_type == "company":
                customer_data = {"Customer_Name": f"{rec.name}", "Tin_Number": f"{rec.vat}", "PulsarAPIAddress": f"{self.env.ref('base.main_company').addis_systems_sales_pubsub_api_address}",
                                 "Namespace": f"{simplified_and_clean_lower_string(rec.name)}_order_and_catalogue"}
                customer_status = requests.post(f"{self.env.ref('base.main_company').addis_systems_client_application_support_api}/AddisSystems/Base/Partner/PulsarStatus", json=customer_data)
                if customer_status and customer_status.status_code == 200 and customer_status.json():
                    rec.sales_pulsar_status = True
                else:
                    rec.sales_pulsar_status = False
            else:
                rec.sales_pulsar_status = False

    @api.depends("name", "vat")
    def addis_systems_stock_pulsar_status(self):
        for rec in self:
            if rec.name and rec.vat and rec.company_type == "company":
                customer_data = {"Customer_Name": f"{rec.name}", "Tin_Number": f"{rec.vat}", "PulsarAPIAddress": f"{self.env.ref('base.main_company').addis_systems_stock_pubsub_api_address}",
                                 "Namespace": f"{simplified_and_clean_lower_string(rec.name)}_picking_and_delivery"}
                customer_status = requests.post(f"{self.env.ref('base.main_company').addis_systems_client_application_support_api}/AddisSystems/Base/Partner/PulsarStatus", json=customer_data)
                if customer_status and customer_status.status_code == 200 and customer_status.json():
                    rec.stock_pulsar_status = True
                else:
                    rec.stock_pulsar_status = False
            else:
                rec.stock_pulsar_status = False

    @api.depends("name", "vat")
    def addis_systems_payment_pulsar_status(self):
        for rec in self:
            if rec.name and rec.vat and rec.company_type == "company":
                customer_data = {"Customer_Name": f"{rec.name}", "Tin_Number": f"{rec.vat}", "PulsarAPIAddress": f"{self.env.ref('base.main_company').addis_systems_payment_pubsub_api_address}",
                                 "Namespace": f"{simplified_and_clean_lower_string(rec.name)}_payment"}
                customer_status = requests.post(f"{self.env.ref('base.main_company').addis_systems_client_application_support_api}/AddisSystems/Base/Partner/PulsarStatus", json=customer_data)
                if customer_status and customer_status.status_code == 200 and customer_status.json():
                    rec.payment_pulsar_status = True
                else:
                    rec.payment_pulsar_status = False
            else:
                rec.payment_pulsar_status = False

    """@api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            action_create = super(AddisSystemsPartnerInherited, self).create(vals)
            if not action_create.vat or action_create.company_type != "company":
                return action_create
            if not action_create.vat.isdigit():
                raise UserError(_("Standard Ethiopian Tin Number can only contain Numerical values"))
            elif len(action_create.vat) not in [13, 10]:
                raise UserError(_("Standard Ethiopian Tin Number should be 10 or 13 digits in length"))
            else:
                return action_create

    def write(self, values):
        action_write = super(AddisSystemsPartnerInherited, self).write(values)

        if not values.get("vat") or values.get("company_type") != "company":
            return action_write
        if not values.get("vat").isdigit():
            raise UserError(_("Standard Ethiopian Tin Number can only contain Numerical values"))
        elif len(values.get("vat")) not in [13, 10]:
            raise UserError(_("Standard Ethiopian Tin Number should be 10 or 13 digits in length"))
        else:
            return action_write
    """

    def addis_systems_get_image_as_base64(self, url):
        try:
            response = requests.get(url, stream=True, verify=False)
            response.raise_for_status()

            if response.headers['content-type'].startswith('image/'):
                image_data = b''
                for chunk in response.iter_content(1024):
                    image_data += chunk
                return base64.b64encode(image_data).decode('utf-8')
            else:
                _logger.error(f"Error Getting Partner Logo: The URL '{url}' does not point to an image.")
                return None
        except requests.exceptions.RequestException as e:
            _logger.error(f"Error Downloading Partner Logo from '{url}': {e}")
            return None

    def addis_systems_exchange_partner_handler(self, partner_data):
        country, state, city, street2, street = partner_data['Company_Address'].split(',') if 'Company_Address' in partner_data else partner_data['address'].split(',')
        latitude, longitude = partner_data['Delivery_Address'].split(',') if 'Delivery_Address' in partner_data else partner_data['location'].split(',')

        partner_name = partner_data['Company_Name'] if 'Company_Name' in partner_data else partner_data['company_name']
        partner_tin = partner_data['Tin_Number'] if 'Tin_Number' in partner_data else partner_data['tin_no']

        partner_id = self.env['res.partner'].search(['|', ('name', '=', partner_name), ('vat', '=', partner_tin)], limit=1)
        if not partner_id:
            new_partner = self.env['res.partner'].create({
                'name': partner_name,
                'company_type': 'company',
                'vat': partner_tin,
                'phone': partner_data['Phone_Number'] if 'Phone_Number' in partner_data else None,

                'website': partner_data['Website'] if 'Website' in partner_data else None,
                'company_registry': partner_data['Vat_Registration_Number'] if 'Vat_Registration_Number' in partner_data else None,
                'email': partner_data['Email'] if 'Email' in partner_data else None,
                'street': street if street != 'False' else None,
                'street2': street2 if street2 != 'False' else None,
                'city': city if city != 'False' else None,
                'state_id': self.env['res.country.state'].search([('name', '=', state), ('country_id', '=', self.env['res.country'].search([('name', '=', country)], limit=1).id)], limit=1).id,
                'country_id': self.env['res.country'].search([('name', '=', country)], limit=1).id,
                'partner_latitude': latitude,
                'partner_longitude': longitude,
                'image_1920': self.addis_systems_get_image_as_base64(partner_data['Company_Logo']),
                'property_purchase_currency_id': self.env['res.currency'].search([('name', '=', partner_data['Currency'])], limit=1).id}
            )
            partner_id = new_partner
        else:
            if not partner_id.phone:
                partner_id.phone = partner_data['Phone_Number']
            if not partner_id.website:
                partner_id.website = partner_data['Website']
            if not partner_id.company_registry:
                partner_id.company_registry = partner_data['Vat_Registration_Number']
            if not partner_id.email:
                partner_id.email = partner_data['Email']
            if not partner_id.street:
                partner_id.street = street if street != 'False' else None
            if not partner_id.street2:
                partner_id.street2 = street2 if street2 != 'False' else None
            if not partner_id.city:
                partner_id.city = city if city != 'False' else None
            if not partner_id.state_id:
                partner_id.state_id = self.env['res.country.state'].search([('name', '=', state)], limit=1).id
            if not partner_id.country_id:
                partner_id.country_id = self.env['res.country.state'].search([('name', '=', country)], limit=1).country_id.id
            if not partner_id.property_purchase_currency_id:
                # partner_id.property_purchase_currency_id = self.env['res.currency'].search([('name', '=', partner_data['Currency'])], limit=1).id
                partner_id.property_purchase_currency_id = self.env['res.currency'].search([('name', '=', 'ETB')], limit=1).id

            partner_id.partner_latitude = latitude
            partner_id.partner_longitude = longitude
            if not partner_id.image_1920:
                partner_id.image_1920 = self.addis_systems_get_image_as_base64(partner_data['Company_Logo'])

        return partner_id
