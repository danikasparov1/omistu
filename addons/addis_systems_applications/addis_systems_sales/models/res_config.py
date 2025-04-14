from odoo import SUPERUSER_ID, _, api, Command, fields, models
from odoo import fields, models, api, _

class AddisSystemsBaseConfigurationResCompanyTHIRDPARTYInherited(models.Model):
    _inherit = "res.company"
    cnet = fields.Boolean(default=True)
    peds = fields.Boolean(default=True)
    maraki = fields.Boolean(default=True)
    cnet_xml_path = fields.Char(string="enter xml path for cnet",required=False,compute="set_cnet_xml_path")
    peds_xml_path = fields.Char(string="enter xml path for peds",required=False,compute="set_peds_xml_path")
    maraki_xml_path = fields.Char(string="enter xml path for maraki",required=False,compute="set_maraki_xml_path")

    @api.model
    def set_cnet_xml_path(self):
        self.cnet_xml_path=self.env['ir.config_parameter'].sudo().get_param('web.base.url')+"/addis_systems_sales/static/data/cnet"
    @api.model
    def set_maraki_xml_path(self):
        self.maraki_xml_path=self.env['ir.config_parameter'].sudo().get_param('web.base.url')+"/addis_systems_sales/static/data/maraki"
    @api.model
    def set_peds_xml_path(self):
        self.peds_xml_path=self.env['ir.config_parameter'].sudo().get_param('web.base.url')+"/addis_systems_sales/static/data/peds"

class ResConfigInheritedThirdParty(models.TransientModel):
    _inherit = "res.config.settings"
    cnet = fields.Boolean(readonly=False,default=lambda self: self.env.ref('base.main_company').cnet)
    peds = fields.Boolean(readonly=False,default=lambda self: self.env.ref('base.main_company').peds)
    maraki = fields.Boolean(readonly=False,default=lambda self: self.env.ref('base.main_company').maraki)
    cnet_xml_path = fields.Char(string="enter xml path for cnet" ,readonly=True,default=lambda self: self.env.ref('base.main_company').cnet_xml_path)
    peds_xml_path = fields.Char(string="enter xml path for peds",readonly=True,default=lambda self: self.env.ref('base.main_company').peds_xml_path)
    maraki_xml_path = fields.Char(string="enter xml path for maraki",readonly=True,default=lambda self: self.env.ref('base.main_company').maraki_xml_path)

    @api.model
    def get_values(self):
        res = super(ResConfigInheritedThirdParty, self).get_values()
        res.update(
            cnet=self.env.ref('base.main_company').cnet,
            peds=self.env.ref('base.main_company').peds,
            maraki=self.env.ref('base.main_company').maraki,
            cnet_xml_path=self.env.ref('base.main_company').cnet_xml_path,
            peds_xml_path=self.env.ref('base.main_company').peds_xml_path,
            maraki_xml_path=self.env.ref('base.main_company').maraki_xml_path,
            
        )
        return res
    def set_values(self):
        super().set_values()
        self.env.ref('base.main_company').cnet=self.cnet
        self.env.ref('base.main_company').peds=self.peds
        self.env.ref('base.main_company').maraki=self.maraki
        self.env.ref('base.main_company').cnet_xml_path=self.cnet_xml_path
        self.env.ref('base.main_company').peds_xml_path=self.peds_xml_path
        self.env.ref('base.main_company').maraki_xml_path=self.maraki_xml_path
