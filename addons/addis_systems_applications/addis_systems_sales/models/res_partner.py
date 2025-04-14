from odoo import SUPERUSER_ID, _, api, Command, fields, models
from odoo.exceptions import ValidationError
from odoo.osv import expression

import re

pattern = r'^\d{10}$|^\d{11}$|^\d{12}$|^\d{10}-\d{1,2}$'

class PartnerInherited(models.Model):
    _inherit = "res.partner"
    _rec_names_search=['phone',"name","vat"]
    partner_code=fields.Char(string="Partner Code")
    customer_code = fields.Char(string="Partner Code")
    vat = fields.Char(string='Tin Number', index=True, help="Tin number format must be like XXXXXXXXXX (10 digits without hyphens) or XXXXXXXXXX-XX (with a hyphen after the 10th digit)")
    # @api.onchange("vat")
    # def partner_format(self):
    #     for record in self:
    #         if record.is_company and record.vat:
    #             vat = record.vat
    #             if re.match(pattern,vat):
    #                 if len(vat)>10:
    #                     if vat[10]!="-":
    #                         vat=vat[:10]+"-"+vat[10:]
    #                         record.vat=vat
    # @api.constrains('vat')
    # def check_vat(self):
    #     vat=self.vat
    #     if self.is_company:
    #         if self.vat:
    #             vat=vat.replace("-","")
    #             if any(v.isalpha() for v   in vat):
    #                 raise ValidationError("Tin number can only contain numbers with optional - after 10 digits")
    #             if not  re.match(pattern,self.vat):   
    #                 raise ValidationError("length of thin number must be 10 or 11 or 12")
    #         else:
    #             raise ValidationError("Tin number is required")
    @api.depends("name")
    def _compute_display_name(self):
        name=""
        for record in self:
            name=record.name or ''
            if record.vat:
                name+=f" [{record.vat}] "
            if record.phone:
                name+=f"[{record.phone}] "
            record.display_name=name

    # @api.model_create_multi
    # def create(self, vals_list):
    #     for vals in vals_list:
    #         if vals.get('partner_code', _("New")) == _("New"):
    #             seq_date = fields.Datetime.context_timestamp(
    #                 self, fields.Datetime.to_datetime(vals['create_date'])
    #             ) if 'create_date' in vals else None
    #             vals['partner_code'] = self.env['ir.sequence'].next_by_code(
    #                 'res.partner', sequence_date=seq_date) or _("New")
    #     return super().create(vals_list)
    @api.model
    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)

        if view_type == 'form':
            for node in arch.xpath(
                "//field[@name='vat']"
            ):
                node.attrib['widget'] = 'tinnumber'

        return arch, view


class Accountmoveinherited(models.Model):
    _inherit="account.move"
    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template for Accounting Moves'),
            'template': '/addis_systems_sales/static/xls/move_entry.xlsx'
        }]        
    