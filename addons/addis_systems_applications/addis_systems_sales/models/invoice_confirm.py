from odoo import fields, models, api, tools, _, SUPERUSER_ID
from odoo.exceptions import ValidationError, AccessError, UserError
from odoo.tools.misc import formatLang
import os 
import xml.etree.ElementTree as ET

class AddisSystemsInvoiceInherited(models.Model):
    _inherit = "account.move"
    cnet_enabled=fields.Boolean(compute="check_cnet")
    maraki_enabled=fields.Boolean(compute="check_maraki")
    peds_enabled=fields.Boolean(compute="check_peds")
    is_xml_downloaded=fields.Boolean(default=False)

    @api.model
    def check_cnet(self):
        for record in self:
            record.cnet_enabled=self.env.ref('base.main_company').cnet
    @api.model
    def check_maraki(self):
        self.maraki_enabled=self.env.ref('base.main_company').maraki
    @api.model
    def check_peds(self):
        self.peds_enabled=self.env.ref('base.main_company').peds

    def action_post(self):
        parent_post = super(AddisSystemsInvoiceInherited, self).action_post()
        return True
        if self.move_type == "out_invoice" or self.move_type == "out_receipt":
            if self.env.ref('base.main_company').cnet:
                self.xml_writer('cnet')
            if self.env.ref('base.main_company').maraki:
                self.xml_writer('maraki')
            if self.env.ref('base.main_company').peds:
                self.xml_writer('peds')          
    
    def download_xml(self):
        if self.state !="posted":
            raise UserError("Record must be in Posted state")
        return{
            'type':"ir.actions.act_url",
            'url':f"/thirdparty/xml/{self.id}",
            'target':'self'
        }

    # those under methods will use and customized when we integrate with third parties like cnet pds maraki ...

    # def download_xml_cnet(self):
    #     if self.state !="posted":
    #         raise UserError("Record must be in Posted state")
    #     if self.env.ref('base.main_company').cnet:
    #         self.xml_writer('cnet')
    #     if self.env.ref('base.main_company').cnet:
    #         name=self.name
    #         name=name.replace("/","_")
    #         path=self.env.ref('base.main_company').cnet_xml_path+"/"+str(self.id)
    #     return{
    #         'type':"ir.actions.act_url",
    #         'url':path,
    #         'target':'new'
    #     }
    
    # def download_xml_maraki(self):
    #     if self.state !="posted":
    #         raise UserError("Record must be in Posted state")
    #     if self.env.ref('base.main_company').maraki:
    #         self.xml_writer('maraki')
    #     if self.env.ref('base.main_company').maraki:
    #         name=self.name
    #         name=name.replace("/","_")
    #         path=self.env.ref('base.main_company').maraki_xml_path+"/"+name+".xml"
    #     if self.env.ref('base.main_company').maraki:
    #         return{
    #             'type':"ir.actions.act_url",
    #             'url':path,
    #             'target':'new'
    #         }
        
        
    # def download_xml_peds(self):
    #     if self.state !="posted":
    #         raise UserError("Record must be in Posted state")
    #     if self.env.ref('base.main_company').peds:
    #         self.xml_writer('peds')
    #     if self.env.ref('base.main_company').peds:
    #         name=self.name
    #         name=name.replace("/","_")
    #         path=self.env.ref('base.main_company').peds_xml_path+"/"+name+".xml"
    #     return{
    #         'type':"ir.actions.act_url",
    #         'url':path,
    #         'target':'new'
    #     }