from odoo import api, fields, models


class MrpProductionInherited(models.Model):
    _inherit = "mrp.production"

    customer_id = fields.Many2one('res.partner', 'Customer Name', domain=[("is_company", "=", False)])
    customer_info=fields.Html("Customer Info",compute="get_customer_info")

    customer_tin_number = fields.Char(related='customer_id.vat', string='Customer TIN Number')
    customer_phone = fields.Char(related='customer_id.phone', string='Customer Phone')
    customer_mobile = fields.Char(related='customer_id.mobile', string='Customer Mobile')
    customer_email = fields.Char(related='customer_id.email', string='Customer Email')

    customer_street = fields.Char(related='customer_id.street', string='Customer Street')
    customer_street2 = fields.Char(related='customer_id.street2', string='Customer Street 2')
    customer_post_office_number = fields.Char(related='customer_id.post_office_number', string='Customer P.O.BOX')
    customer_house_number = fields.Char(related='customer_id.house_number', string='Customer House Number')
    customer_kebele = fields.Char(related='customer_id.kebele', string='Customer Kebele')
    customer_woreda = fields.Char(related='customer_id.woreda', string='Customer Woreda')
    customer_sub_city = fields.Char(related='customer_id.sub_city', string='Customer Sub-City')
    customer_city = fields.Char(related='customer_id.city', string='Customer City')
    customer_zip = fields.Char(related='customer_id.zip', string='Customer ZIP Code')
    customer_zone_id = fields.Many2one(related='customer_id.zone_id', string='Customer Zone')
    customer_state_id = fields.Many2one(related='customer_id.state_id', string='Customer State')
    customer_country_id = fields.Many2one(related='customer_id.country_id', string='Customer Country')

    @api.depends('customer_id')
    def get_customer_info(self):
        for record in self:
            vat = record.customer_id.vat
            phone = record.customer_id.phone
            contact_address = record.customer_id.contact_address
            cust_info = ""
            if vat:
                cust_info += f"<b>Tin no</b> : {vat}<br>"
            if phone:
                cust_info += f"<b>phone</b> : {phone}<br>"
            if contact_address and contact_address.strip():
                cust_info += f"<b>Address : </b> {contact_address}"
            record.customer_info = cust_info

    def action_open_wizard(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("addis_systems_manufacturing.addis_systems_manufacturing_production_customer_information_action")
        action['res_id'] = self.id
        return action

    def download_report(self):
        action = self.env["ir.actions.report"]._for_xml_id("mrp.action_report_production_order")
        self.ensure_one()
        return action
