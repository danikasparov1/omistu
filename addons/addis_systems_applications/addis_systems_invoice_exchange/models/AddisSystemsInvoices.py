from odoo import fields, models, api, tools, _, SUPERUSER_ID
from odoo.exceptions import ValidationError, AccessError, UserError
from odoo.tools.misc import formatLang
from pulsar.exceptions import ConnectError, PulsarException, AuthenticationError, NotConnected

from pulsar import Client
import avro.schema
import avro.io
import logging
from num2words import num2words
import requests
import threading
import time
import os
import re
import io
import asyncio


def parse_avro_schema(schema_file_path):
    with open(schema_file_path, 'r') as schema_file:
        schema_str = schema_file.read()
    return avro.schema.parse(schema_str)


def simplified_and_clean_lower_string(string):
    return re.sub(r'\W+', '', string).lower()


_logger = logging.getLogger(__name__)

class AddisSystemsCompanyInherited(models.Model):
    _inherit = 'res.company'
    addis_system_id=fields.Char(default="2ceb0dfcdb1beff6")
    addis_systems_requests_timeout = fields.Integer(string="Request Time Out", required=True, default=int(tools.config['addis_systems_requests_timeout']) or 20)

    addis_systems_client_application_support_api_secure = fields.Boolean(string="Secure Support API (SSL)", default=bool(tools.config['addis_systems_client_application_support_api_secure']))
    addis_systems_client_application_support_api = fields.Char(string="Support API URL", required=True, default=str(tools.config['addis_systems_client_application_support_api']) or "http://127.0.0.1:8080")

    addis_systems_service_url_secure = fields.Boolean(string="Secure Service (SSL)", default=bool(tools.config['addis_systems_service_url_secure']))
    addis_systems_service_url = fields.Char(string="Services URL", required=True, default=str(tools.config['addis_systems_service_url']) or "http://127.0.0.1:8080")

    addis_systems_pubsub_secure = fields.Boolean(string="Secure Pulsar (TLS)", default=bool(tools.config['addis_systems_pubsub_secure']))

    addis_systems_invoice_pubsub_address = fields.Char(string="Invoice Exchange Pulsar Address", required=True, default=str(tools.config['addis_systems_invoice_pubsub_address']) or "pulsar://127.0.0.1:6650")
    addis_systems_invoice_pubsub_api_address = fields.Char(string="Invoice Exchange Pulsar API Address", required=True, default=str(tools.config['addis_systems_invoice_pubsub_api_address']) or "http://127.0.0.1:8084")

    addis_systems_sales_pubsub_address = fields.Char(string="Sales Exchange Pulsar Address", required=True, default=str(tools.config['addis_systems_sales_pubsub_address']) or "pulsar://127.0.0.1:6650")
    addis_systems_sales_pubsub_api_address = fields.Char(string="Sales Exchange Pulsar API Address", required=True, default=str(tools.config['addis_systems_sales_pubsub_api_address']) or "http://127.0.0.1:8084")

    addis_systems_stock_pubsub_address = fields.Char(string="Stock Exchange Pulsar Address", required=True, default=str(tools.config['addis_systems_stock_pubsub_address']) or "pulsar://127.0.0.1:6650")
    addis_systems_stock_pubsub_api_address = fields.Char(string="Stock Exchange Pulsar API Address", required=True, default=str(tools.config['addis_systems_stock_pubsub_api_address']) or "http://127.0.0.1:8084")

    addis_systems_payment_pubsub_address = fields.Char(string="Payment Exchange Pulsar Address", required=True, default=str(tools.config['addis_systems_payment_pubsub_address']) or "pulsar://127.0.0.1:6650")
    addis_systems_payment_pubsub_api_address = fields.Char(string="Payment Exchange Pulsar API Address", required=True, default=str(tools.config['addis_systems_payment_pubsub_api_address']) or "http://127.0.0.1:8084")

    invoice_pulsar_status = fields.Boolean(string="Invoice Pulsar Configured", default=False, compute="addis_systems_invoice_pulsar_status", store=False)
    sales_pulsar_status = fields.Boolean(string="Sales Pulsar Configured", default=False, compute="addis_systems_sales_pulsar_status", store=False)
    stock_pulsar_status = fields.Boolean(string="Stock Pulsar Configured", default=False, compute="addis_systems_stock_pulsar_status", store=False)
    payment_pulsar_status = fields.Boolean(string="Payment Pulsar Configured", default=False, compute="addis_systems_payment_pulsar_status", store=False)

    @api.depends("name", "vat", "addis_system_id")
    def addis_systems_invoice_pulsar_status(self):
        if (base_company := self.env.ref('base.main_company')) and self.id == base_company.id and base_company.name and base_company.vat and base_company.addis_system_id:
            simplify_name = simplified_and_clean_lower_string(base_company.name)
            tenant = str(base_company.addis_system_id)
            client = Client(f"{str(base_company.addis_systems_invoice_pubsub_address)}")

            for topic in ['invoice_acknowledgement', 'bill', 'refund_acknowledgement', 'refund']:
                try:
                    topic_name = f"persistent://{tenant}/{simplify_name}_invoice_and_payment/{simplify_name}_{topic}"
                    subscription_name = f"{simplify_name}_{str(base_company.addis_system_id)}"
                    consumer = client.subscribe(topic_name, subscription_name)
                    if consumer.is_connected():
                        base_company.invoice_pulsar_status = True
                    else:
                        base_company.invoice_pulsar_status = False
                        return
                    consumer.close()
                except PulsarException as e:
                    if "NoSuchNamespaceException" in str(e):
                        base_company.invoice_pulsar_status = False
                        _logger.error("No such namespace 'invoice' exists for company %s In Invoice Exchange Pulsar Address %s", str(base_company.name), str(base_company.addis_systems_invoice_pubsub_address))
                        return
                    else:
                        base_company.invoice_pulsar_status = False
                        _logger.error("No such namespace 'invoice' exists for company %s In Invoice Exchange Pulsar Address %s", str(base_company.name), str(base_company.addis_systems_invoice_pubsub_address))
                        return
        else:
            self.invoice_pulsar_status = False
            _logger.error("Company %s is missing mandatory fields to start Addis Systems Services", base_company.name)

    @api.depends("name", "vat", "addis_system_id")
    def addis_systems_sales_pulsar_status(self):
        if (base_company := self.env.ref('base.main_company')) and self.id == base_company.id and base_company.name and base_company.vat and base_company.addis_system_id:
            simplify_name = simplified_and_clean_lower_string(base_company.name)
            tenant = str(base_company.addis_system_id)
            client = Client(f"{str(base_company.addis_systems_sales_pubsub_address)}")

            for topic in ['catalogue_requests', 'catalogue', 'price_request', 'price_update', 'purchase_order', 'sales_order']:
                try:
                    topic_name = f"persistent://{tenant}/{simplify_name}_order_and_catalogue/{simplify_name}_{topic}"
                    subscription_name = f"{simplify_name}_{str(base_company.addis_system_id)}"
                    consumer = client.subscribe(topic_name, subscription_name)
                    if consumer.is_connected():
                        base_company.sales_pulsar_status = True
                    else:
                        base_company.sales_pulsar_status = False
                        return
                    consumer.close()
                except PulsarException as e:
                    if "NoSuchNamespaceException" in str(e):
                        base_company.sales_pulsar_status = False
                        _logger.error("No such namespace 'order_and_catalogue' exists for company %s In Sales Exchange Pulsar Address %s", str(base_company.name), str(base_company.addis_systems_sales_pubsub_address))
                        return
                    else:
                        base_company.sales_pulsar_status = False
                        _logger.error("No such namespace 'order_and_catalogue' exists for company %s In Sales Exchange Pulsar Address %s", str(base_company.name), str(base_company.addis_systems_sales_pubsub_address))
                        return
        else:
            self.sales_pulsar_status = False
            _logger.error("Company %s is missing mandatory fields to start Addis Systems Services", base_company.name)

    @api.depends("name", "vat", "addis_system_id")
    def addis_systems_stock_pulsar_status(self):
        if (base_company := self.env.ref('base.main_company')) and self.id == base_company.id and base_company.name and base_company.vat and base_company.addis_system_id:
            simplify_name = simplified_and_clean_lower_string(base_company.name)
            tenant = str(base_company.addis_system_id)
            client = Client(f"{str(base_company.addis_systems_stock_pubsub_address)}")

            for topic in ['picking_order', 'picking_order_confirmation', 'delivery_order', 'delivery_order_confirmation']:
                try:
                    topic_name = f"persistent://{tenant}/{simplify_name}_picking_and_delivery/{simplify_name}_{topic}"
                    subscription_name = f"{simplify_name}_{str(base_company.addis_system_id)}"
                    consumer = client.subscribe(topic_name, subscription_name)
                    if consumer.is_connected():
                        base_company.stock_pulsar_status = True
                    else:
                        base_company.stock_pulsar_status = False
                        return
                    consumer.close()
                except PulsarException as e:
                    if "NoSuchNamespaceException" in str(e):
                        base_company.stock_pulsar_status = False
                        _logger.error("No such namespace 'picking_and_delivery' exists for company %s In Stock Exchange Pulsar Address %s", str(base_company.name), str(base_company.addis_systems_stock_pubsub_address))
                        return
                    else:
                        base_company.stock_pulsar_status = False
                        _logger.error("No such namespace 'picking_and_delivery' exists for company %s In Stock Exchange Pulsar Address %s", str(base_company.name), str(base_company.addis_systems_stock_pubsub_address))
                        return
        else:
            self.stock_pulsar_status = False
            _logger.error("Company %s is missing mandatory fields to start Addis Systems Services", base_company.name)

    @api.depends("name", "vat", "addis_system_id")
    def addis_systems_payment_pulsar_status(self):
        if (base_company := self.env.ref('base.main_company')) and self.id == base_company.id and base_company.name and base_company.vat and base_company.addis_system_id:
            simplify_name = simplified_and_clean_lower_string(base_company.name)
            tenant = str(base_company.addis_system_id)
            client = Client(f"{str(base_company.addis_systems_payment_pubsub_address)}")

            for topic in ['received']:
                try:
                    topic_name = f"persistent://{tenant}/{simplify_name}_payment/{topic}"
                    subscription_name = f"{simplify_name}_{str(base_company.addis_system_id)}"
                    consumer = client.subscribe(topic_name, subscription_name)
                    if consumer.is_connected():
                        base_company.payment_pulsar_status = True
                    else:
                        base_company.payment_pulsar_status = False
                        return
                    consumer.close()
                except PulsarException as e:
                    if "NoSuchNamespaceException" in str(e):
                        base_company.payment_pulsar_status = False
                        _logger.error("No such namespace 'payment' exists for company %s In Payment Exchange Pulsar Address %s", str(base_company.name), str(base_company.addis_systems_payment_pubsub_address))
                        return
                    else:
                        base_company.payment_pulsar_status = False
                        _logger.error("No such namespace 'payment' exists for company %s In Payment Exchange Pulsar Address %s", str(base_company.name), str(base_company.addis_systems_payment_pubsub_address))
                        return
        else:
            self.payment_pulsar_status = False
            _logger.error("Company %s is missing mandatory fields to start Addis Systems Services", base_company.name)


class AddisSystemsPartnerInherited(models.Model):
    _inherit = 'res.partner'

    # TODO Change option to the brand name (When branded)

    ubl_cii_format = fields.Selection(
        selection_add=[('addis_e_invoice', "Addis ET")])

    @api.model
    def _get_ubl_cii_formats(self):
        action_get_ubl = super(AddisSystemsPartnerInherited, self)._get_ubl_cii_formats()
        action_get_ubl["ET"] = "addis_e_invoice"
        return action_get_ubl


class AddisSystemsInvoiceLineInherited(models.Model):
    _inherit = "account.move.line"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'price_unit' in vals and float(vals['price_unit']) <= 0.0:
                raise ValidationError("Price can not be 0 or Negative")
            if 'quantity' in vals and float(vals['quantity']) <= 0.0:
                raise ValidationError("Quantity can not be 0 or Negative")
        return super(AddisSystemsInvoiceLineInherited, self).create(vals_list)

    def write(self, vals):
        if 'price_unit' in vals and float(vals['price_unit']) <= 0.0:
            raise ValidationError("Price can not be 0 or Negative")
        if 'quantity' in vals and float(vals['quantity']) <= 0.0:
            raise ValidationError("Quantity can not be 0 or Negative")

        return super(AddisSystemsInvoiceLineInherited, self).write(vals)


class AddisSystemsInvoiceInherited(models.Model):
    _inherit = "account.move"

    @api.onchange("partner_id")
    def partner_filter(self):
        return {"domain": {"partner_id": [("id", "!=", self.company_id.partner_id.id)]}}

    Invoice_Registration_Number = fields.Char(string="Invoice Registration Number")
    acknowledgement_number = fields.Char(string="Acknowledgement Number")
    acknowledgement_date = fields.Char(string="Acknowledgement Date")
    signed_invoice = fields.Char(string="Signed Invoice")
    signed_qr_code = fields.Char(string="Signed QR Code")
    created_date = fields.Char(string="Created Date")
    created_by = fields.Char(string="Created By")
    invoice_status = fields.Selection([("pending", "Pending"), ("registered", "Registered"), ("failed", "Failed")], required=True, readonly=True, copy=False, tracking=True, default="pending")

    electronic_invoicing = fields.Boolean(string="E-invoicing Sent", default=False)
    partner_electronic_invoicing = fields.Boolean(string="is E-Invoice User", default=False)

    # ------------------------------------------------------------
    # Invoice Addis Systems Report Methods
    # ------------------------------------------------------------

    def amount_in_words(self, data):
        return str(num2words(data)).title()

    def signed_invoice_decode_for_print(self, signed_qr_code):
        payment_json = {
            "invoice_reference": self.name,
            "customer": self.partner_id.name,
            "customer_tin": self.partner_id.vat,
        }
        return str(payment_json)

    # ------------------------------------------------------------
    # TODO Addis Systems Invoice Producer and Consumer
    # NOTE Below Functions Will Listen to topic on Addis Systems Pulsar for Invoice, create a record and Produce Invoice on Send
    # ------------------------------------------------------------

    # ------------------------------------------------------------
    # Addis Systems Invoice/Refund Register
    # ------------------------------------------------------------

    def addis_systems_invoice_registration(self):
        invoice_line = []
        line_sequence_number = 0
        for line in self.invoice_line_ids:
            line_sequence_number = line_sequence_number + 1
            invoice_line.append(
                {
                    "sno": str(line_sequence_number),
                    "hsncode": "",
                    "barcode": str(line.product_id.barcode),
                    "invoicing_policy": str(line.product_id.product_tmpl_id.invoice_policy),
                    "Product_desc": str(line.product_id.product_tmpl_id.description_sale or ""),
                    "product_name": str(line.product_id.product_tmpl_id.name),
                    "product_type": str(line.product_id.product_tmpl_id.detailed_type),
                    "product_category": str(line.product_id.product_tmpl_id.categ_id.name),
                    "qty": str(line.quantity),
                    "unit": str(line.product_uom_id.name),
                    "unit_price": str(line.price_unit),
                    "amount_type": str(line.tax_ids.amount_type if line.tax_ids else ""),
                    "tax_type": str(line.tax_ids.type_tax_use if line.tax_ids else ""),
                    "tax_scope": str(line.tax_ids.tax_scope if line.tax_ids else ""),
                    "tax_amount": str(line.tax_ids.amount if line.tax_ids else ""),
                    "Line_allowance_code": "",
                    "Line_allowance_reason": "",
                    "Line_allowance_amount": "",
                    "Line_charge_code": "",
                    "Line_charge_reason": "",
                    "Line_charge_amount": "",
                    "total_price": str(line.price_subtotal or ""),
                }
            )

        invoice_data = {
            "Invoice_Reference": {
                "Buy_ref_no": "",
                "Project_ref_no": "",
                "cont_ref_no": "",
                "PO_ref_no": "",
                "Sellers_order_ref_no": str(self.name or ""),
                "Rec_advice_ref_no": "",
                "Disp_advice_ref_no": "",
                "Tender_ref_no": str(self.ref),
                "Invo_obj_ref_no": str(self.name or ""),
                "invoice_declaration": "",
            },
            "Invoice_Desc": {
                "taxschema": str(fields.datetime.now()),
                "InvType": str(self.move_type),
                "Invoice_no": str(self.id),
                "Invoice_ref": str(self.name),
                "Inv_Dt": str(self.invoice_date or ""),
                "payment_due_Dt": str(self.invoice_date_due or ""),
            },
            "Invoice_source_process": {
                "process": "AR",
                "SupType": "B2B",
                "proccess_reference_no": "",
            },
            "Seller": {
                "tin_no": str(self.company_id.vat or ""),
                "license_number": str(self.company_id.company_registry or ""),
                "vat_reg_no": str(self.company_id.company_registry or ""),
                "vat_reg_Dt": "WHOLESALE",
                "address": str(f'{self.company_id.country_id.name},{self.company_id.state_id.name},{self.company_id.city},{self.company_id.street2},{self.company_id.street}'),
                "location": str(f"{self.company_id.partner_id.partner_latitude},{self.company_id.partner_id.partner_longitude}"),
                "email": str(self.company_id.email or ""),
                "company_name": str(self.env.company.name),
                "user_name": str(self.env.user.name),
            },
            "Buyer": {
                "tin_no": str(self.partner_id.vat or ""),
                "vat_reg_no": str(self.partner_id.vat or ""),
                "address": str(self.partner_id.country_id.name or ""),
                "location": str(self.partner_id.state_id.name or ""),
                "phone_no": str(self.partner_id.phone or None),
                "email": str(self.partner_id.email or None),
                "company_name": str(self.partner_id.name),
            },
            "Payee": {
                "id": "",
                "name": str(self.payment_reference or ""),
                "registration_number": "",
                "bank": "",
                "bank_account": "",
                "legal_registration": "",
            },
            "Delivery_info": {
                "Delivery_note_number": "",
                "delivery_date": "",
                "delivery_location": "",
                "delivery_address": "",
            },
            "Payment_info": {
                "payment_means": "",
                "payer_account": "",
                "payment_term": "",
            },
            "Invoice_total": str(self.amount_total or ""),
            "Vat_breakdown": {
                "Vat_category_code": "",
                "Vat_reason_code": "",
                "Vat_reason_text": "",
                "Vat_breakdown_amount": str(self.amount_tax or ""),
            },
            "Invoice_allowance": "",
            "Invoice_charge": "",
            "Invoice_line": invoice_line,
        }

        invoice_register_request = requests.post(
            f"{self.env.ref('base.main_company').addis_systems_client_application_support_api}/AddisSystems/Invoice/InvoiceRegister/", json=invoice_data)
        print(f"{self.env.ref('base.main_company').addis_systems_client_application_support_api}/AddisSystems/Invoice/InvoiceRegister/")
        print(invoice_data)
        print(invoice_register_request.json())
        return invoice_register_request.json() if invoice_register_request.status_code == 200 and invoice_register_request else False

    def addis_systems_refund_registration(self):
        refund_line = []

        line_sequence_number = 0
        for line in self.invoice_line_ids:
            line_sequence_number = line_sequence_number + 1
            refund_line.append(
                {
                    "sno": str(line_sequence_number) if self.move_type else "",
                    "hsncode": "",
                    "barcode": str(line.product_id.barcode) if self.move_type else "",
                    "invoicing_policy": str(line.product_id.product_tmpl_id.invoice_policy) if self.move_type else "",
                    "Product_desc": str(line.product_id.product_tmpl_id.description_sale) if self.move_type else "",
                    "product_name": str(line.product_id.product_tmpl_id.name) if self.move_type else "",
                    "product_type": str(line.product_id.product_tmpl_id.detailed_type) if self.move_type else "",
                    "product_category": str(line.product_id.product_tmpl_id.categ_id.name) if self.move_type else "",
                    "qty": str(line.quantity) if self.move_type else "",
                    "unit": str(line.product_uom_id.name) if self.move_type else "",
                    "unit_price": str(line.price_unit) if self.move_type else "",
                    "amount_type": str(line.tax_ids.amount_type) if self.move_type else "",
                    "tax_type": str(line.tax_ids.type_tax_use) if self.move_type else "",
                    "tax_scope": str(line.tax_ids.tax_scope) if self.move_type else "",
                    "tax_amount": str(line.tax_ids.amount) if self.move_type else "",
                    "Line_allowance_code": "",
                    "Line_allowance_reason": "",
                    "Line_allowance_amount": "",
                    "Line_charge_code": "",
                    "Line_charge_reason": "",
                    "Line_charge_amount": "",
                    "total_price": str(line.price_subtotal) if self.move_type else "",
                }
            )
        refund_data = {
            "Invoice_Reference": {
                "Buy_ref_no": str(self.name) if self.name else "",
                "Seller_ref_no": str(self.reversed_entry_id.ref) if self.reversed_entry_id.ref else "",
                "invoice_declaration": "",
            },
            "Invoice_Desc": {
                "taxschema": str(fields.datetime.now()),
                "InvType": str(self.move_type) if self.move_type else "",
                "Invoice_no": str(self.id) if self.id else "",
                "Invoice_ref": str(self.name) if self.name else "",
                "Inv_Dt": str(self.invoice_date) if self.invoice_date else "",
                "payment_due_Dt": str(self.invoice_date_due) if self.invoice_date_due else ""
            },
            "Invoice_source_process": {
                "process": "AR",
                "SupType": "B2B",
                "proccess_reference_no": "",
            },
            "Seller": {
                "tin_no": str(self.partner_id.vat) if self.partner_id.vat else "",
                "license_number": "",
                "vat_reg_no": "",
                "vat_reg_Dt": "",
                "address": "",
                "company_name": str(self.partner_id.name),
                "user_name": str(self.env.user.name) if self.env.user.name else "",
            },
            "Buyer": {
                "tin_no": str(self.env.company.vat) if self.env.company.vat else "",
                "vat_reg_no": str(self.env.company.vat) if self.env.company.vat else "",
                "address": str(self.env.company.name) if self.env.company.name else "",
                "location": str(self.env.company.vat) if self.env.company.vat else "",
                "phone_no": str(self.env.company.phone) if self.env.company.phone else "",
                "email": str(self.env.company.email) if self.env.company.email else "",
                "company_name": str(self.env.company.name),
            },
            "Invoice_total": str(self.amount_total) if self.amount_total else "",
            "Vat_breakdown": {
                "Vat_category_code": "",
                "Vat_reason_code": "",
                "Vat_reason_text": "",
                "Vat_breakdown_amount": str(self.amount_tax) if self.amount_tax else "",
            },
            "Invoice_allowance": "",
            "Invoice_charge": "",
            "Invoice_line": refund_line,
        }

        refund_register_request = requests.post(
            f"{self.env.ref('base.main_company').addis_systems_client_application_support_api}/AddisSystems/Refund/RefundRegister/", json=refund_data)
        return refund_register_request.json() if refund_register_request.status_code == 200 and refund_register_request else False

    def action_post(self):
        main_company = self.env.ref('base.main_company')
        parent_post = super(AddisSystemsInvoiceInherited, self).action_post()

        if self.move_type == "out_invoice":
            # NOTE ---------------------- Registering Invoice ----------------------
            invoice_registration_detail = None
            try:
                invoice_registration_detail = self.addis_systems_invoice_registration()
            except Exception as e:
                _logger.warning(
                    " %s:Addis Systems Invoice Exchange Message Send Fail for %s", e, self.partner_id.name)
                self.electronic_invoicing = False
                raise AccessError(
                    "Couldn't Sent the Invoice to %s", self.partner_id.name)
            finally:
                if invoice_registration_detail:
                    self.Invoice_Registration_Number = invoice_registration_detail["IRN"]
                    self.acknowledgement_number = invoice_registration_detail["AckNo"]
                    self.acknowledgement_date = invoice_registration_detail["AckDt"]
                    self.signed_invoice = invoice_registration_detail["Signed_invoice"]
                    self.signed_qr_code = invoice_registration_detail["Signed_QRCode"]
                    self.created_date = invoice_registration_detail["Created_Date"]
                    self.created_by = invoice_registration_detail["Created_by"]
                    self.invoice_status = ("registered" if invoice_registration_detail["Inv_Status"] == "registered" else "failed")
                    self.partner_electronic_invoicing = True
                    return parent_post
                else:
                    raise AccessError("Couldn't register the Invoice, Please Try again")
        elif self.move_type == "in_invoice" and self.acknowledgement_number:
            api_endpoint = f"{main_company.addis_systems_client_application_support_api}/invoice/change-status/{self.acknowledgement_number}"

            print()
            print(api_endpoint)
            print()
            requests.patch(api_endpoint)
        elif self.move_type == "in_refund":
            # NOTE ---------------------- Registering Refund ----------------------
            refund_registration_detail = None
            try:
                refund_registration_detail = self.addis_systems_refund_registration()
            except Exception as e:
                _logger.warning(
                    " %s:Addis Systems Refund Exchange Message Send Fail for %s", e, self.partner_id.name)
                self.electronic_invoicing = False
                raise AccessError(
                    "Couldn't Sent the Refund to %s", self.partner_id.name)
            finally:
                if refund_registration_detail:
                    self.Invoice_Registration_Number = refund_registration_detail["IRN"]
                    self.acknowledgement_number = refund_registration_detail["AckNo"]
                    self.acknowledgement_date = refund_registration_detail["AckDt"]
                    self.signed_invoice = refund_registration_detail["Signed_invoice"]
                    self.signed_qr_code = refund_registration_detail["Signed_QRCode"]
                    self.created_date = refund_registration_detail["Created_Date"]
                    self.created_by = refund_registration_detail["Created_by"]
                    self.invoice_status = (
                        "registered" if refund_registration_detail["Inv_Status"] == "registered" else "failed")
                    self.partner_electronic_invoicing = True
                    return parent_post
                else:
                    raise AccessError(
                        "Couldn't register the Refund, Please Try again")
        elif self.move_type == "out_refund" and self.acknowledgement_number:
            # NOTE at a time of updating invoice exchange received
            # TODO
            api_endpoint = f"{main_company.addis_systems_client_application_support_api}/refund/change-status/{self.acknowledgement_number}"
            requests.patch(api_endpoint)
        else:
            return parent_post

    # ------------------------------------------------------------
    # Addis Systems Invoice/Refund Exchange
    # ------------------------------------------------------------

    def _electronic_invoice_message(self, partner):
        invoice_data = {
            "IRN": self.Invoice_Registration_Number or "",
            "AckNo": self.acknowledgement_number if self.Invoice_Registration_Number else "",
            "AckDt": self.acknowledgement_date or "",
            "Signed_invoice": self.signed_invoice or "",
            "Created_Date": self.created_date or "",
            "Created_by": self.created_by or "",
            "Inv_Status": self.invoice_status.lower() if self.invoice_status else "",
            "Signed_QRCode": self.signed_qr_code or "",
            "Buyer": str(partner.name),
            "Buyer_Tin": str(partner.vat),
            "Seller": str(self.env.company.name),
            "Seller_Tin": str(self.env.company.vat)
        }

        sent_request = requests.post(
            f"{self.env.ref('base.main_company').addis_systems_client_application_support_api}/AddisSystems/Invoice/InvoiceExchange/", json=invoice_data)
        return True if sent_request.status_code == 200 and sent_request.json() else False

    def send_electronic_invoice_to_partner(self):
        if self.env.ref('base.main_company').invoice_pulsar_status and self.name != _('New'):
            if self.partner_id.invoice_pulsar_status:
                e_invoice_sent = None

                try:
                    e_invoice_sent = self._electronic_invoice_message(self.partner_id)
                except Exception as e:
                    _logger.warning(" %s:Addis Systems Invoice Exchange Message Send Fail for %s", e, self.partner_id.name)
                    self.electronic_invoicing = False
                    raise AccessError("Couldn't Sent the Invoice to %s", self.partner_id.name)
                finally:
                    if e_invoice_sent:
                        self.electronic_invoicing = True
                        msg_topic = _("Message Produced Successfully to partner %s", self.partner_id.name)
                        self.message_post(subject=msg_topic,
                                          body=_("The Partner '%s' Will receive the message very shortly", self.partner_id.name),
                                          message_type="notification",
                                          partner_ids=[self.env.user.id],
                                          subtype_xmlid="mail.mt_note")
                    elif not e_invoice_sent and not self.electronic_invoicing:
                        raise UserError("Unable to process data, Check the Invoice have all the data required")
            else:
                msg_topic = _("Message Produced Not Successfully to partner %s", self.partner_id.name)
                self.message_post(subject=msg_topic,
                                  body=_("The Partner '%s' Doesn't have exchange", self.partner_id.name),
                                  message_type="notification",
                                  partner_ids=[self.env.user.id],
                                  subtype_xmlid="mail.mt_comment")

    def _electronic_refund_message(self, partner):
        refund_data = {
            "IRN": self.Invoice_Registration_Number or "",
            "AckNo": self.acknowledgement_number if self.Invoice_Registration_Number else "",
            "AckDt": self.acknowledgement_date or "",
            "Signed_invoice": self.signed_invoice or "",
            "Created_Date": self.created_date or "",
            "Created_by": self.created_by or "",
            "Inv_Status": self.invoice_status.lower() if self.invoice_status else "",
            "Signed_QRCode": self.signed_qr_code or "",
            "Buyer": str(self.env.company.name),
            "Buyer_Tin": str(self.env.company.vat),
            "Seller": str(partner.name),
            "Seller_Tin": str(partner.vat)
        }

        sent_request = requests.post(
            f"{self.env.ref('base.main_company').addis_systems_client_application_support_api}/AddisSystems/Invoice/RefundExchange/", json=refund_data)
        return True if sent_request.status_code == 200 and sent_request.json() else False

    def send_electronic_refund_to_partner(self):
        if self.env.ref('base.main_company').invoice_pulsar_status and self.name != _('New'):
            if self.partner_id.invoice_pulsar_status:
                e_refund_sent = None

                try:
                    e_refund_sent = self._electronic_refund_message(
                        self.partner_id)
                except Exception as e:
                    _logger.warning(
                        " %s:Addis Systems Refund Exchange Message Send Fail for %s", e, self.partner_id.name)
                    self.electronic_invoicing = False
                    raise AccessError(
                        "Couldn't Sent the Refund to %s", self.partner_id.name)
                finally:
                    if e_refund_sent:
                        self.electronic_invoicing = True
                        msg_topic = _(
                            "Message Produced Successfully to partner %s", self.partner_id.name)
                        self.message_post(subject=msg_topic,
                                          body=_(
                                              "The Partner '%s' Will receive the message very shortly", self.partner_id.name),
                                          message_type="notification",
                                          partner_ids=[self.env.user.id],
                                          subtype_xmlid="mail.mt_comment")
                    elif not e_refund_sent and not self.electronic_invoicing:
                        raise UserError(
                            "Unable to process data, Check the Refund have all the data required")
            else:
                msg_topic = _(
                    "Message Produced Not Successfully to partner %s", self.partner_id.name)
                self.message_post(subject=msg_topic,
                                  body=_(
                                      "The Partner '%s' Doesn't have exchange", self.partner_id.name),
                                  message_type="notification",
                                  partner_ids=[self.env.user.id],
                                  subtype_xmlid="mail.mt_comment")

    # ------------------------------------------------------------
    # Addis Systems Invoice/Refund Consumers
    # ------------------------------------------------------------

    def addis_system_invoice_and_refund_consumer_init(self):
        if (main_company := self.env.ref('base.main_company', False)) and main_company.invoice_pulsar_status:
            all_active_thread_names = [
                thread.name for thread in threading.enumerate()]

            invoice_thread_name = f"addis_systems_{main_company.vat}_invoice_consumer"
            refund_thread_name = f"addis_systems_{main_company.vat}_refund_consumer"
            if invoice_thread_name not in all_active_thread_names:
                catalogue_request_thread = threading.Thread(target=self._addis_systems_invoice_consumer, args=([invoice_thread_name]))
                catalogue_request_thread.name = invoice_thread_name
                catalogue_request_thread.start()

            if refund_thread_name not in all_active_thread_names:
                catalogue_request_thread = threading.Thread(target=self._addis_systems_refund_consumer, args=([refund_thread_name]))
                catalogue_request_thread.name = refund_thread_name
                catalogue_request_thread.start()

            time.sleep(2)

    # ----------------------- Invoice -----------------------

    def invoice_exchange_decoder(self, acknowledgement_number, main_company):
        api_end_point = f"{main_company.addis_systems_service_url}/getInvoice/{acknowledgement_number}"

        print()
        print(api_end_point)
        print()
        response = requests.get(api_end_point, timeout=main_company.addis_systems_requests_timeout)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 400:
            response_meaning = "Record is not found"
            _logger.error("Addis Systems %s Invoice couldn't be decoded:%s:%s", acknowledgement_number, response.status_code, response_meaning)
            return False
        elif response.status_code == 502:
            response_meaning = "Bad Gateway"
            _logger.error("Addis Systems %s Invoice couldn't be decoded:%s:%s", acknowledgement_number, response.status_code, response_meaning)
            return False
        else:
            response_meaning = "API End Point is not responding"
            _logger.error("Addis Systems %s Invoice couldn't be decoded:%s:%s", acknowledgement_number, response.status_code, response_meaning)
            return False

    def addis_systems_exchange_vendor_bill_create(self, vb_mor_data, vb_decoded_data):
        invoice_reference = vb_decoded_data["Invoice_Reference"]
        invoice_description = vb_decoded_data["Invoice_Desc"]
        invoice_source_process = vb_decoded_data["Invoice_source_process"]
        seller_info = vb_decoded_data["Seller"]
        buyer_info = vb_decoded_data["Buyer"]
        payee_info = vb_decoded_data["Payee"]
        delivery_info = vb_decoded_data["Delivery_info"]
        payment_info = vb_decoded_data["Payment_info"]
        vat_description = vb_decoded_data["Vat_breakdown"]

        with self.env.registry.cursor() as new_cr:
            env = api.Environment(new_cr, SUPERUSER_ID, {})
            partner_id = env['res.partner'].addis_systems_exchange_partner_handler(
                seller_info)

            if partner_id and not env["account.move"].search([("acknowledgement_number", "=", vb_mor_data["AckNo"])]):
                tender_ref = env["purchase.order"].search([("name", "=", invoice_reference['Tender_ref_no'])])

                vendor_bill_vals = {
                    "partner_id": partner_id.id,
                    "invoice_date": invoice_description["Inv_Dt"],
                    "invoice_date_due": invoice_description["payment_due_Dt"],
                    "payment_reference": payee_info['name'],
                    "purchase_id": tender_ref.id or None,
                    "Invoice_Registration_Number": vb_mor_data["IRN"],
                    "acknowledgement_number": vb_mor_data["AckNo"],
                    "acknowledgement_date": vb_mor_data["AckDt"],
                    "signed_invoice": vb_mor_data["Signed_invoice"],
                    "signed_qr_code": vb_mor_data["Signed_QRCode"],
                    "created_date": vb_mor_data["Created_Date"],
                    "created_by": vb_mor_data["Created_by"],
                    "invoice_status": vb_mor_data["Inv_Status"],
                    "move_type": "in_invoice",
                    "ref": invoice_description["Invoice_ref"],
                    "to_check": True,
                    "amount_tax": vat_description["Vat_breakdown_amount"],
                    "state": "draft",
                    "company_id": self.env.company.id,
                    "invoice_incoterm_id": tender_ref.incoterm_id.id or None
                }

                account_move = env["account.move"].create(vendor_bill_vals)

                product_lines = []

                for products in vb_decoded_data["Invoice_line"]:
                    product = env["product.template"].search([("name", "=", products["hsncode"])], limit=1) or env["product.template"].create(
                        {
                            "name": products["product_name"],
                            "sale_ok": False,
                            "purchase_ok": True,
                            "invoice_policy": products["invoicing_policy"],
                            "description_purchase": products["Product_desc"],
                            "detailed_type": products["product_type"],
                            "list_price": products["unit_price"],
                            "standard_price": products["unit_price"],
                        }
                    )

                    tax_id = env["account.tax"].search([("amount_type", "=", products["amount_type"]), (
                        "type_tax_use", "!=", products["tax_type"]), ("amount", "=", products["tax_amount"])], limit=1)
                    prod_line = {
                        "product_id": env["product.product"].search([("product_tmpl_id", "=", product.id)], limit=1).id,
                        "quantity": products["qty"],
                        "price_unit": products["unit_price"],
                        "tax_ids": tax_id or None,
                        "move_id": account_move.id,
                    }

                    product_lines.append(prod_line)

                env["account.move.line"].create(product_lines)

                accountant_manager_group_users = env.ref(
                    "account.group_account_manager").users
                for user in accountant_manager_group_users:
                    dead_line = account_move.invoice_date_due or account_move.date
                    activity_type = env.ref("mail.mail_activity_data_todo")
                    for activity in activity_type:
                        env["mail.activity"].create(
                            {
                                "display_name": "Addis Systems Vendor Bill",
                                "summary": _("New Vendor Bill to Confirm from %s", account_move.partner_id.name),
                                "date_deadline": dead_line,
                                "user_id": user.id,
                                "res_id": account_move.id,
                                "res_model_id": env.ref("account.model_account_move").id,
                                "activity_type_id": activity.id,
                            }
                        )
                return account_move

    def _addis_systems_invoice_consumer(self, thread_name):
        with self.env.registry.cursor() as new_cr:
            env = api.Environment(new_cr, SUPERUSER_ID, {})
            main_company = env.ref('base.main_company', False)
            invoice_ack_schema = parse_avro_schema(f'{os.path.dirname(os.path.abspath(__file__))}/schemas/InvoiceAcknowledgmentSchema.avsc')
            simplify_name = simplified_and_clean_lower_string(main_company.name)
            service_url = env.ref('base.main_company').addis_systems_sales_pubsub_address
            topic_name = f"persistent://{main_company.addis_system_id}/{simplify_name}_invoice_and_payment/{simplify_name}_bill"
            subscription_name = f"{simplify_name}"

            client = Client(service_url)
            consumer = client.subscribe(topic_name, subscription_name)
            while True:
                msg = consumer.receive()
                bytes_writer = io.BytesIO(msg.data())
                decoder = avro.io.BinaryDecoder(bytes_writer)
                datum_reader = avro.io.DatumReader(invoice_ack_schema)
                invoice_ack_data = datum_reader.read(decoder)

                if invoice_ack_data and invoice_ack_data["Signed_invoice"]:
                    if decoded_bill := env['account.move'].invoice_exchange_decoder(invoice_ack_data["AckNo"], main_company):
                        if env['account.move'].addis_systems_exchange_vendor_bill_create(invoice_ack_data, decoded_bill):
                            consumer.acknowledge(msg)

    # ----------------------- Refund -----------------------

    def credit_note_exchange_decoder(self, acknowledgement_number, main_company):
        api_end_point = f"{main_company.addis_systems_service_url}/getRefund/{acknowledgement_number}"

        response = requests.get(
            api_end_point, timeout=main_company.addis_systems_requests_timeout)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 400:
            if response.json() == "Invoice already cleared":
                response_meaning = "Record is not found"
                _logger.error("Addis Systems %s Refund couldn't be decoded:%s:%s",
                              acknowledgement_number, response.status_code, response_meaning)
            else:
                response_meaning = "Record is not found"
                _logger.error("Addis Systems %s Refund couldn't be decoded:%s:%s",
                              acknowledgement_number, response.status_code, response_meaning)
            return False
        elif response.status_code == 502:
            response_meaning = "Bad Gateway"
            _logger.error("Addis Systems %s Refund couldn't be decoded:%s:%s",
                          acknowledgement_number, response.status_code, response_meaning)
            return False
        else:
            response_meaning = "API End Point is not responding"
            _logger.error("Addis Systems %s Refund couldn't be decoded:%s:%s",
                          acknowledgement_number, response.status_code, response_meaning)
            return False

    def addis_systems_exchange_credit_note_create(self, vb_mor_data, vb_decoded_data):
        refund_reference = vb_decoded_data["Invoice_Reference"]
        refund_description = vb_decoded_data["Invoice_Desc"]
        refund_source_process = vb_decoded_data["Invoice_source_process"]
        seller_info = vb_decoded_data["Seller"]
        buyer_info = vb_decoded_data["Buyer"]
        vat_description = vb_decoded_data["Vat_breakdown"]

        with self.env.registry.cursor() as new_cr:
            env = api.Environment(new_cr, SUPERUSER_ID, {})
            invoice_record = env["account.move"].search(
                [("name", "=", refund_reference["Seller_ref_no"])])
            if not env["account.move"].search([("acknowledgement_number", "=", vb_mor_data["AckNo"])]) and invoice_record:
                credit_bill_vals = {
                    "partner_id": invoice_record.partner_id.id,
                    "invoice_date": refund_description["Inv_Dt"],
                    "invoice_date_due": refund_description["payment_due_Dt"],
                    "payment_reference": "",
                    "reversed_entry_id": invoice_record.id,
                    "Invoice_Registration_Number": vb_mor_data["IRN"],
                    "acknowledgement_number": vb_mor_data["AckNo"],
                    "acknowledgement_date": vb_mor_data["AckDt"],
                    "signed_invoice": vb_mor_data["Signed_invoice"],
                    "signed_qr_code": vb_mor_data["Signed_QRCode"],
                    "created_date": vb_mor_data["Created_Date"],
                    "created_by": vb_mor_data["Created_by"],
                    "invoice_status": vb_mor_data["Inv_Status"],
                    "move_type": "out_refund",
                    "ref": refund_reference["Buy_ref_no"],
                    "to_check": True,
                    "amount_tax": vat_description["Vat_breakdown_amount"],
                    "state": "draft",
                    "company_id": self.env.company.id,
                }

                credit_note = env["account.move"].create(credit_bill_vals)

                product_lines = []

                for products in vb_decoded_data["Invoice_line"]:
                    product = env["product.template"].search([("name", "=", products["product_name"])], limit=1) or env["product.template"].create(
                        {
                            "name": products["product_name"],
                            "sale_ok": False,
                            "purchase_ok": True,
                            "invoice_policy": products["invoicing_policy"],
                            "description_purchase": products["Product_desc"],
                            "detailed_type": products["product_type"],
                            "list_price": products["unit_price"],
                            "standard_price": products["unit_price"],
                        }
                    )

                    tax_id = env["account.tax"].search([("amount_type", "=", products["amount_type"]), (
                        "type_tax_use", "!=", products["tax_type"]), ("amount", "=", products["tax_amount"])], limit=1)
                    product_line = {
                        "product_id": env["product.product"].search([("product_tmpl_id", "=", product.id)], limit=1).id,
                        "quantity": products["qty"],
                        "price_unit": products["unit_price"],
                        "tax_ids": tax_id or None,
                        "move_id": credit_note.id,
                    }
                    product_lines.append(product_line)

                env["account.move.line"].create(product_lines)

                accountant_manager_group_users = env.ref(
                    "account.group_account_manager").users
                for user in accountant_manager_group_users:
                    dead_line = credit_note.invoice_date_due or credit_note.date
                    activity_type = env.ref("mail.mail_activity_data_todo")
                    for activity in activity_type:
                        env["mail.activity"].create(
                            {
                                "display_name": "Addis Systems Vendor Bill",
                                "summary": _("New Refund Bill to Confirm from %s", credit_note.partner_id.name),
                                "date_deadline": dead_line,
                                "user_id": user.id,
                                "res_id": credit_note.id,
                                "res_model_id": env.ref("account.model_account_move").id,
                                "activity_type_id": activity.id,
                            }
                        )
                return credit_note

    def _addis_systems_refund_consumer(self, thread_name):
        with self.env.registry.cursor() as new_cr:
            env = api.Environment(new_cr, SUPERUSER_ID, {})
            main_company = env.ref('base.main_company', False)
            refund_ack_schema = parse_avro_schema(
                f'{os.path.dirname(os.path.abspath(__file__))}/schemas/RefundAcknowledgmentSchema.avsc')
            simplify_name = simplified_and_clean_lower_string(
                main_company.name)
            service_url = env.ref(
                'base.main_company').addis_systems_sales_pubsub_address
            topic_name = f"persistent://{main_company.addis_system_id}/{simplify_name}_invoice_and_payment/{simplify_name}_refund"
            subscription_name = f"{simplify_name}"

            client = Client(service_url)
            consumer = client.subscribe(topic_name, subscription_name)
            while True:
                msg = consumer.receive()
                bytes_writer = io.BytesIO(msg.data())
                decoder = avro.io.BinaryDecoder(bytes_writer)
                datum_reader = avro.io.DatumReader(refund_ack_schema)
                refund_ack_data = datum_reader.read(decoder)

                if refund_ack_data and refund_ack_data["Signed_invoice"]:
                    if decoded_refund := env['account.move'].credit_note_exchange_decoder(refund_ack_data["AckNo"], main_company):
                        if env['account.move'].addis_systems_exchange_credit_note_create(refund_ack_data, decoded_refund):
                            consumer.acknowledge(msg)
