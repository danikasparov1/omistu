from odoo import api, fields, models, _, Command
class MrpProductionInherited(models.Model):
    _inherit="mrp.production"
    customer=fields.Many2one('res.partner', 'Customer Name',domain=[("is_company","=",False)])
    customer_info=fields.Html("Customer Info",compute="get_customer_info")
    product_request_count = fields.Integer(string="Product Requests",compute='_get_product_request_count')

    @api.depends('customer')
    def get_customer_info(self):
        for record in self:
            vat = record.customer.vat
            phone = record.customer.phone 
            contact_address = record.customer.contact_address
            cust_info=""
            if vat:
                cust_info+=f"<b>Tin no</b> : {vat}<br>"
            if phone:
                cust_info+=f"<b>phone</b> : {phone}<br>"
            if contact_address and contact_address.strip():
                cust_info+=f"<b>Address : </b> {contact_address}"
            record.customer_info=cust_info

    def open_manufacturing_requests(self):
        # Return an action to open the desired form view
        domain=[('manufacturing_order','=',self.id)]
        context = dict(self.env.context)
        context.update({
        'search_default_manufacturing_order': self.id,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Custom Form View',
            'res_model': 'addisystems.product.request',  # Replace with your target model
            'view_mode': 'tree,form',
            'domain':domain,
            'target': 'self',  # Opens the form in a modal popup. Use 'current' for normal navigation.
            'context': context,
        }
    def _get_product_request_count(self):
        for record in self:
            record.product_request_count=self.env['addisystems.product.request'].search_count([("manufacturing_order",'=',record.id)])


    def action_open_wizard(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("addis_systems_manufacturing.mrp_production_action_inherited")
        action['res_id'] = self.id
        return action
    
    def download_report(self):
        action = self.env["ir.actions.report"]._for_xml_id("mrp.action_report_production_order")
        self.ensure_one()
        return action
    
    def action_open_product_request_form(self):
        # Return an action to open the desired form view
        context = dict(self.env.context)
        context.update({
        'default_manufacturing_order': self.id,  # Pre-fill the manufacturing order ID in the product request form
    })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Custom Form View',
            'res_model': 'addisystems.product.request',  # Replace with your target model
            'view_mode': 'form',
            'target': 'new',  # Opens the form in a modal popup. Use 'current' for normal navigation.
            'context': context,
        }
    

