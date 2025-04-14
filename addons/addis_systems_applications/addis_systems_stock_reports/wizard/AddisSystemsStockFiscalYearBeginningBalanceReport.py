from odoo import fields, models, api

import datetime


class AddisSystemsStockCardReport(models.TransientModel):
    _name = 'report.fiscal.year.beginning.balance'
    _description = 'Addis Systems Stock Fiscal Year Beginning Balance'

    company_id = fields.Many2one('res.company', string='Company', readonly=True, required=True, default=lambda self: self.env.company)
    fiscal_year = fields.Many2one('account.fiscal.year', string="Fiscal Year", required=True, check_company=True)

    fiscal_year_opening_date = fields.Date(related='fiscal_year.date_from', string="Fiscal Year Opening Date")
    fiscal_year_closing_date = fields.Date(related='fiscal_year.date_to', string="Fiscal Year Closing Date")

    stock_locations = fields.Many2many('stock.location', string='Locations', compute="_compute_company_locations", inverse="_inverse_company_locations")
    all_products = fields.Many2many('product.product', string='All Products', compute="_compute_all_company_products")

    pre_period_product_moves = fields.One2many('stock.move.line', compute='_pre_period_start_stock_moves')
    period_product_moves = fields.One2many('stock.move.line', compute='_post_period_start_stock_moves')

    @api.depends('company_id')
    def _compute_company_locations(self):
        for rec in self:
            if rec.company_id:
                rec.stock_locations = self.env['stock.location'].search([('company_id', '=', rec.company_id.id)]).ids

    def _inverse_pls_fields_str(self):
        pass

    @api.depends('company_id')
    def _compute_all_company_products(self):
        for rec in self:
            if rec.company_id:
                rec.all_products = self.env['product.product'].search(['|', ('company_id', '=', rec.company_id.id), ('company_id', '=', None), '|', ('sale_ok', '=', True), ('purchase_ok', '=', True)]).ids

    @api.depends('company_id', 'fiscal_year', 'fiscal_year_opening_date', 'fiscal_year_closing_date')
    def _pre_period_start_stock_moves(self):
        for rec in self:
            if rec.fiscal_year_opening_date:
                fiscal_year_opening_datetime = datetime.datetime.combine(rec.fiscal_year_opening_date, datetime.time(23, 4, 0))
                rec.pre_period_product_moves = self.env['stock.move.line'].search([('state', '=', 'done'), ('date', '<', fiscal_year_opening_datetime)], order='date DESC')
            else:
                rec.pre_period_product_moves = None

    @api.depends('company_id', 'fiscal_year', 'fiscal_year_opening_date', 'fiscal_year_closing_date')
    def _post_period_start_stock_moves(self):
        for rec in self:
            if rec.fiscal_year_opening_date:
                fiscal_year_opening_datetime = datetime.datetime.combine(rec.fiscal_year_opening_date, datetime.time(23, 4, 0))
                rec.period_product_moves = self.env['stock.move.line'].search([('state', '=', 'done'), ('date', '>=', fiscal_year_opening_datetime)], order='date DESC')
            else:
                rec.period_product_moves = None

    # NOTE Process Data

    def preview_html(self):
        return self.env.ref('addis_systems_stock_reports.report_addis_systems_fiscal_year_beginning_balance_report_html').report_action(self)

    def process_pdf(self):
        return self.env.ref('addis_systems_stock_reports.report_addis_systems_fiscal_year_beginning_balance_report_pdf').report_action(self)

    def process_excel(self):
        pass
