
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from num2words import num2words

class PaymentRequest(models.Model):
    _name = 'payment.request'
    _description = 'Payment Request'

    payment_for = fields.Many2one(
        'res.partner', 
        string='Payment For', 
        required=True, 
        # default=lambda self: self.env.user.partner_id,
        # readonly=True
    )
    department_id = fields.Many2one(
        'hr.department', 
        string='Department', 
        readonly=True,
        default=lambda self: self._get_user_department()
    )

    payment_for_new = fields.Selection(
        [('administrator', 'Administrator'), ('employee', 'Employee'), ('vendor', 'Vendor')],
        string="Payment For",
        # required=True
    )
    payment_reason = fields.Text(string='Payment Reason', required=True)
    request_date = fields.Date(string='Date', default=fields.Date.today, required=True)
    amount = fields.Float(string='Amount', required=True)
    amount_in_words = fields.Char(string="Amount in Words", compute="_compute_amount_in_words", store=True)
    # tax_deduction = fields.Float(string='Tax Deduction')

    # tax_type = fields.Selection(
    #     [('vat', 'VAT'), ('tot', 'TOT'), ('wht', 'WHT')],
    #     string='Tax Type',
    #     required=True
    # )

    # tax_type = fields.Selection(
    #     selection='_get_tax_types',
    #     string='Tax Type',
    #     required=True
    # )

    tax_type = fields.Many2many(
        'account.tax',
        string='Tax Type',
        required=True
    )
    # tax_deduction = fields.Float(string='Tax Deduction', compute="_compute_tax_deduction", store=True)
    # vat = fields.Float(string='VAT (%)')
    # withholding_amount = fields.Float(string='Withholding Amount')
    # total_amount = fields.Float(string='Total Amount', compute='_compute_total_amount', store=True)

    tax_deduction = fields.Float(string='Tax Deduction', compute="_compute_tax_deduction", store=True)
    vat = fields.Float(string='VAT (%)', compute="_compute_vat", store=True)
    withholding_amount = fields.Float(string='Withholding Amount', compute="_compute_withholding", store=True)
    total_amount = fields.Float(string='Total Amount', compute='_compute_total_amount', store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], default='draft', string='Status')
    @api.depends('amount', 'tax_type')
    def _compute_tax_deduction(self):
        for record in self:
            if record.tax_type == 'vat':
                record.tax_deduction = record.amount * 0.15  # Example VAT rate of 15%
            elif record.tax_type == 'tot':
                record.tax_deduction = record.amount * 0.05  # Example TOT rate of 5%
            elif record.tax_type == 'wht':
                record.tax_deduction = record.amount * 0.10  # Example WHT rate of 10%
            else:
                record.tax_deduction = 0.0


    # @api.model
    # def _get_tax_types(self):
    #     taxes = self.env['account.tax'].search([])
    #     return [(tax.id, tax.name) for tax in taxes]

    def _get_user_department(self):
        """
        Fetches the department of the logged-in user based on the related employee record.
        """
        employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        return employee.department_id.id if employee else False

    @api.depends('amount')
    def _compute_amount_in_words(self):
        for record in self:
            record.amount_in_words = num2words(record.amount, lang='en').capitalize() if record.amount else ''

    # @api.depends('amount', 'tax_deduction', 'vat', 'withholding_amount')
    # def _compute_total_amount(self):
    #     for record in self:
    #         vat_amount = (record.amount * record.vat) / 100 if record.vat else 0
    #         deductions = record.tax_deduction + vat_amount + record.withholding_amount
    #         record.total_amount = record.amount - deductions


    # @api.depends('amount', 'tax_type')
    # def _compute_tax_deduction(self):
    #     for record in self:
    #         tax = self.env['account.tax'].browse(record.tax_type)
    #         if tax:
    #             record.tax_deduction = record.amount * (tax.amount / 100)
    #         else:
    #             record.tax_deduction = 0.0

    # @api.depends('amount', 'tax_deduction', 'vat', 'withholding_amount')
    # def _compute_total_amount(self):
    #     for record in self:
    #         vat_amount = (record.amount * record.vat) / 100 if record.vat else 0
    #         deductions = record.tax_deduction + vat_amount + record.withholding_amount
    #         record.total_amount = record.amount - deductions

    @api.depends('amount', 'tax_type')
    def _compute_tax_deduction(self):
        for record in self:
            tax_deduction = 0.0
            for tax in record.tax_type:
                tax_deduction += record.amount * (tax.amount / 100)
            record.tax_deduction = tax_deduction

    @api.depends('amount', 'tax_type')
    def _compute_vat(self):
        for record in self:
            vat_amount = 0.0
            for tax in record.tax_type:
                if tax.tax_group_id.name == 'VAT':
                    vat_amount += record.amount * (tax.amount / 100)
            record.vat = vat_amount

    @api.depends('amount', 'tax_type')
    def _compute_withholding(self):
        for record in self:
            withholding_amount = 0.0
            for tax in record.tax_type:
                if tax.tax_group_id.name == 'Withholding':
                    withholding_amount += record.amount * (tax.amount / 100)
            record.withholding_amount = withholding_amount

    @api.depends('amount', 'tax_deduction', 'vat', 'withholding_amount')
    def _compute_total_amount(self):
        for record in self:
            deductions = record.tax_deduction + record.vat + record.withholding_amount
            record.total_amount = record.amount - deductions



    def action_create_payment_order(self):
        self.state = 'approved'
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Payment Order',
            'res_model': 'payment.order.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_payment_for': self.payment_for_new,
                'default_payment_reason': self.payment_reason,
                'default_amount': self.amount,
                'default_date': self.request_date,
            }
        }

    def action_approve(self):
        for request in self:
            request.state = 'approved'
            # Logic to create an accounting entry can be added here
            self.env['account.move'].create({
                'move_type': 'out_invoice',
                'partner_id': self.env.user.partner_id.id,  # Assuming partner_id is required
                'invoice_line_ids': [(0, 0, {'product_id': False, 'name': request.payment_reason, 'price_unit': request.amount, 'quantity': 1})],
            })

    def action_pay(self):
        for request in self:
            if request.state != 'approved':
                raise UserError("You can only pay approved requests.")
            request.state = 'done'

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_print_report(self):
        return self.env.ref('payment_request.action_report_payment_request').report_action(self)


    

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class PaymentOrderWizard(models.TransientModel):
    _name = 'payment.order.wizard'
    _description = 'Payment Order Wizard'

    payment_for = fields.Selection(
        [('employee', 'Employee'), ('supplier', 'Supplier'), ('other', 'Other')],
        string="Payment For",
        required=True
    )
    payment_reason = fields.Text(string="Payment Reason", required=True)
    date = fields.Date(string="Date", default=fields.Date.context_today, required=True)
    amount = fields.Float(string="Amount", required=True)
    debit_account_id = fields.Many2one(
        'account.account',
        string="Debit Account",
        domain="[('account_type', '=', 'asset_cash')]",  # Updated for Odoo 17
        # required=True
    )
    journal_id = fields.Many2one('account.journal', string="Journal")

    def action_create_payment_order(self):
        self.ensure_one()
        self.env['payment.order'].create({
            'payment_for': self.payment_for,
            'payment_reason': self.payment_reason,
            'amount': self.amount,
            'date': self.date,
            'debit_account_id': self.debit_account_id.id,
            'journal_id': self.journal_id.id,
        })
        return {'type': 'ir.actions.act_window_close'}

