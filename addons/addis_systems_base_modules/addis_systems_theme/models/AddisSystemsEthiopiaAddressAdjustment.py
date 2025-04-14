from email.policy import default

from odoo import models, fields, api, _
from odoo.exceptions import UserError

from collections import defaultdict

ADDRESS_FIELDS = ('post_office_number', 'street', 'street2', 'house_number', 'kebele', 'woreda', 'sub_city', 'city', 'zone_id', 'state_id', 'country_id')


class AddisSystemsCountryInherited(models.Model):
    _inherit = 'res.country'

    name_am = fields.Char(string='የሀገር ስም', required=False, translate=False)

    @api.constrains('address_format')
    def _check_address_format(self):
        for record in self:
            if record.address_format:
                address_fields = self.env['res.partner']._formatting_address_fields() + ['zone_name', 'state_code', 'state_name', 'country_code', 'country_name', 'company_name']
                try:
                    record.address_format % {i: 1 for i in address_fields}
                except (ValueError, KeyError):
                    raise UserError(_('The layout contains an invalid format key'))


class AddisSystemsCountryStateInherited(models.Model):
    _inherit = 'res.country.state'

    capital_city = fields.Char(string="Capital City", required=False)
    name_am = fields.Char(string='የክልል ስም', required=False,
                          help='የአንድ ሀገር አስተዳደራዊ ክፍሎች. ለምሳሌ. ፌደሬሽን ግዛት, መምሪያ, ካንቶን')


class AddisSystemsCountryStatesZone(models.Model):
    _name = 'res.country.state.zone'
    _description = 'Country State Zone (Ethiopia Case)'
    _order = 'name'

    name = fields.Char(string='Zone Name', required=True, translate=False)
    name_am = fields.Char(string='የዞን ስም', required=False, translate=False)
    country_id = fields.Many2one('res.country', string='Country', required=True)
    state_id = fields.Many2one('res.country.state', string='State', required=True)


class AddisSystemsEthiopiaAddressAdjustmentInCompany(models.Model):
    _inherit = 'res.company'

    trade_name = fields.Char(string="Trade Name ", readonly=False, required=True, compute='_compute_trade_name', inverse='_inverse_trade_name')
    vat = fields.Char(related='partner_id.vat', string="Tin Number", readonly=False)

    post_office_number = fields.Char(string="P.O.BOX", compute='_compute_address', inverse='_inverse_post_office_number')
    house_number = fields.Char(string="House Number", compute='_compute_address', inverse='_inverse_house_number')

    kebele = fields.Char(string="Kebele", compute='_compute_address', inverse='_inverse_kebele')
    woreda = fields.Char(string="Woreda", compute='_compute_address', inverse='_inverse_woreda')

    sub_city = fields.Char(string="Sub-City", compute='_compute_address', inverse='_inverse_sub_city')
    zone_id = fields.Many2one("res.country.state.zone", string='Zone', ondelete='restrict', domain="[('state_id', '=?', state_id), ('country_id', '=?', country_id)]", compute='_compute_address', inverse='_inverse_zone_id')

    def _get_company_address_field_names(self):
        """ Return a list of fields coming from the address partner to match
        on company address fields. Fields are labeled same on both models. """
        return ['street', 'street2', 'post_office_number', 'house_number', 'kebele', 'woreda', 'sub_city', 'city', 'zip', 'zone_id','state_id', 'country_id']

    def _get_company_address_update(self, partner):
        return dict((fname, partner[fname]) for fname in self._get_company_address_field_names())

    # TODO @api.depends(): currently now way to formulate the dependency on the
    # partner's contact address
    def _compute_address(self):
        for company in self.filtered(lambda company: company.partner_id):
            address_data = company.partner_id.sudo().address_get(adr_pref=['contact'])
            if address_data['contact']:
                partner = company.partner_id.browse(address_data['contact']).sudo()
                company.update(company._get_company_address_update(partner))

    def _compute_trade_name(self):
        for company in self.filtered(lambda company: company.partner_id):
            address_data = company.partner_id.sudo().address_get(adr_pref=['contact'])
            if address_data['contact']:
                partner = company.partner_id.browse(address_data['contact']).sudo()
                company.update({'trade_name': partner['trade_name']})

    def _inverse_trade_name(self):
        for company in self:
            company.partner_id.trade_name = company.trade_name

    def _inverse_post_office_number(self):
        for company in self:
            company.partner_id.post_office_number = company.post_office_number

    def _inverse_house_number(self):
        for company in self:
            company.partner_id.house_number = company.house_number

    def _inverse_kebele(self):
        for company in self:
            company.partner_id.kebele = company.kebele

    def _inverse_woreda(self):
        for company in self:
            company.partner_id.woreda = company.woreda

    def _inverse_sub_city(self):
        for company in self:
            company.partner_id.sub_city = company.sub_city

    def _inverse_zone_id(self):
        for company in self:
            company.partner_id.zone_id = company.zone_id


class AddisSystemsEthiopiaAddressAdjustmentInPartner(models.Model):
    _inherit = 'res.partner'

    trade_name = fields.Char(string="Trade Name ", readonly=False, required=True, default=lambda self: self.env.company.name)
    vat = fields.Char(string="Tin Number", readonly=False, required=False)

    house_number = fields.Char(string="House Number")
    post_office_number = fields.Char(string="P.O.BOX")

    kebele = fields.Char(string="Kebele")
    woreda = fields.Char(string="Woreda")

    sub_city = fields.Char(string="Sub-City")
    zone_id = fields.Many2one("res.country.state.zone", string='Zone', ondelete='restrict', domain="[('state_id', '=?', state_id), ('country_id', '=?', country_id)]")

    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict', default=lambda self: self.env.company.country_id.id)

    @api.onchange('state_id')
    def _addis_onchange_state_id(self):
        if not self.state_id:
            self.zone_id = None
        elif self.state_id and self.zone_id:
            if self.zone_id.state_id != self.state_id:
                self.zone_id = None

    @api.model
    def _address_fields(self):
        """Returns the list of address fields that are synced from the parent."""
        return list(ADDRESS_FIELDS)

    def _prepare_display_address(self, without_company=False):
        # get the information that will be injected into the display format
        # get the address format
        address_format = self._get_address_format()
        args = defaultdict(str, {
            'zone_name': self._get_zone_name(),
            'state_code': self.state_id.code or '',
            'state_name': self.state_id.name or '',
            'country_code': self.country_id.code or '',
            'country_name': self._get_country_name(),
            'company_name': self.commercial_company_name or '',
        })
        for field in self._formatting_address_fields():
            args[field] = self[field] or ''
        if without_company:
            args['company_name'] = ''
        elif self.commercial_company_name:
            address_format = '%(company_name)s\n' + address_format
        return address_format, args

    def _get_zone_name(self):
        return self.zone_id.name or ''

    @api.model
    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type in ['tree', 'pivot', 'graph', 'form']:
            for node in arch.xpath("//field[@name='vat']"):
                node.set('string', _("Tin Number"))
        return arch, view
