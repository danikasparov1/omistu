from reportlab.lib.pagesizes import landscape

from odoo import models, fields

class PayrollReportWizard(models.TransientModel):
    _name = 'hr.payroll.report1'
    _description = 'Payroll Report Wizard'

    employee = fields.Boolean(string='Employee', default=True)
    department_id = fields.Boolean(string="Department" , default=True)
    bank_account_id = fields.Boolean(string="Bank Account", default=True)
    period = fields.Boolean(string="Period", default=True)
    monthly_basic_salary = fields.Boolean(string="Monthly Basic Salary")

    total_working_days = fields.Boolean(string="Total Working Days")
    total_day_worked = fields.Boolean(string="Total Day Worked")
    payslip_run_name = fields.Boolean(string="Month Of Payroll")
    structure = fields.Boolean(string="Structure")
    payslip_name = fields.Boolean(string="Payslip Name")

    basic = fields.Boolean(string="BASIC(USD)")
    basic_etb = fields.Boolean(string="BASIC(ETB)",default=True)
    gross = fields.Boolean(string="GROSS", default=True)
    net = fields.Boolean(string="NET", default=True)
    pension = fields.Boolean(string="Employee Pension (7%)", default=True)

    pension_comp = fields.Boolean(string="Employer Pension(11%)", default=True)
    tax = fields.Boolean(string="Income Tax", default=True)
    total_deduction = fields.Boolean(string="Total Deduction", default=True)
    overtime = fields.Boolean(string="Overtime")
    hra = fields.Boolean(string="HRA")


    da = fields.Boolean(string="Professional Allowance")
    travel_allowance = fields.Boolean(string="Transport Allowance")
    travel_allowance_notax = fields.Boolean(string="None Taxable Transport Allowance")
    meal_allowance = fields.Boolean(string="Meal Allowance")
    medical_allowance = fields.Boolean(string="Medical Allowance")

    communication_allowance = fields.Boolean(string="Communication Allowance")
    internet_allowance = fields.Boolean(string="Internet Allowance")
    fuel_allowance = fields.Boolean(string="Fuel Allowance")
    unused_leave_payment = fields.Boolean(string="Unused Leave Payment")
    severance_pay_compensation = fields.Boolean(string="Severance Pay Compensation")

    training_development = fields.Boolean(string="Training And Development")
    position_allowance = fields.Boolean(string="Position Allowance")
    desert_allowance = fields.Boolean(string="Desert Allowance")
    representation_allowance = fields.Boolean(string="Representation Allowance")
    taxable_salary = fields.Boolean(string="Taxable Salary", default=True)

    total_payment = fields.Boolean(string="Severance net payment ")
    total_adjusted_payout = fields.Boolean(string="Severance TAX payment ")
    expense = fields.Boolean(string="Expense")
    loan = fields.Boolean(string="Loan")
    advance_salary = fields.Boolean(string="Advance Salary")

    bonus = fields.Boolean(string="Bonus")
    status = fields.Boolean(string="Status")
    updated_on = fields.Boolean(string="Updated On")
    created_on = fields.Boolean(string="Created Date")
    last_updated = fields.Boolean(string="Last Updated")
    provident_employee = fields.Boolean(string="Employee Provident Fund", default=True)

    provident_employer = fields.Boolean(string="Employer Provident Fund", default=True)
    total_provident = fields.Boolean(string="Total Provident Fund", default=True)
    payroll_ids = fields.Many2many("custom.hr.payroll.report")

    def action_print_report(self):
        data = {
            'payroll_ids':self.payroll_ids.ids,
            'employee': self.employee,
            'department_id': self.department_id,
            'bank_account_id': self.bank_account_id,
            'period': self.period,
            'monthly_basic_salary': self.monthly_basic_salary,
            'total_working_days': self.total_working_days,
            'total_day_worked': self.total_day_worked,
            'payslip_run_name': self.payslip_run_name,
            'structure': self.structure,
            'payslip_name': self.payslip_name,
            'basic': self.basic,
            'basic_etb': self.basic_etb,
            'gross': self.gross,
            'net': self.net,
            'pension': self.pension,
            'pension_comp': self.pension_comp,
            'tax': self.tax,
            'total_deduction': self.total_deduction,
            'overtime': self.overtime,
            'hra': self.hra,
            'da': self.da,
            'travel_allowance': self.travel_allowance,
            'travel_allowance_notax': self.travel_allowance_notax,
            'meal_allowance': self.meal_allowance,
            'medical_allowance': self.medical_allowance,
            'communication_allowance': self.communication_allowance,
            'internet_allowance': self.internet_allowance,
            'fuel_allowance': self.fuel_allowance,
            'unused_leave_payment': self.unused_leave_payment,
            'severance_pay_compensation': self.severance_pay_compensation,
            'training_development': self.training_development,
            'position_allowance': self.position_allowance,
            'desert_allowance': self.desert_allowance,
            'representation_allowance': self.representation_allowance,
            'taxable_salary': self.taxable_salary,
            'total_payment': self.total_payment,
            'total_adjusted_payout': self.total_adjusted_payout,
            'expense': self.expense,
            'loan': self.loan,
            'advance_salary': self.advance_salary,
            'bonus': self.bonus,
            'status': self.status,
            'updated_on': self.updated_on,
            'created_on': self.created_on,
            'last_updated': self.last_updated,
            'provident_employee': self.provident_employee,
            'provident_employer': self.provident_employer,
            'total_provident': self.total_provident
        }

        return self.env.ref('custom_hr_payroll_report.payroll_report_action_id').with_context(landscape=True).report_action(self, data=data)

class HrPayrollReportPDF(models.AbstractModel):
    _name = 'report.custom_hr_payroll_report.hr_report_template_id'

    def _get_report_values(self, docids, data=None):
        domain = [('status', '!=', 'cancel'),('id', 'in',data.get('payroll_ids') )]

        docs = self.env['custom.hr.payroll.report'].search(domain)
        colum = {
            'employee': data.get('employee'),
            'department_id': data.get('department_id'),
            'bank_account_id': data.get('bank_account_id'),
            'period': data.get('period'),
            'monthly_basic_salary': data.get('monthly_basic_salary'),
            'total_working_days': data.get('total_working_days'),
            'total_day_worked': data.get('total_day_worked'),
            'payslip_run_name': data.get('payslip_run_name'),
            'structure': data.get('structure'),
            'payslip_name': data.get('payslip_name'),
            'basic': data.get('basic'),
            'basic_etb': data.get('basic_etb'),
            'gross': data.get('gross'),
            'net': data.get('net'),
            'pension': data.get('pension'),
            'pension_comp': data.get('pension_comp'),
            'tax': data.get('tax'),
            'total_deduction': data.get('total_deduction'),
            'overtime': data.get('overtime'),
            'hra': data.get('hra'),
            'da': data.get('da'),
            'travel_allowance': data.get('travel_allowance'),
            'travel_allowance_notax': data.get('travel_allowance_notax'),
            'meal_allowance': data.get('meal_allowance'),
            'medical_allowance': data.get('medical_allowance'),
            'communication_allowance': data.get('communication_allowance'),
            'internet_allowance': data.get('internet_allowance'),
            'fuel_allowance': data.get('fuel_allowance'),
            'unused_leave_payment': data.get('unused_leave_payment'),
            'severance_pay_compensation': data.get('severance_pay_compensation'),
            'training_development': data.get('training_development'),
            'position_allowance': data.get('position_allowance'),
            'desert_allowance': data.get('desert_allowance'),
            'representation_allowance': data.get('representation_allowance'),
            'taxable_salary': data.get('taxable_salary'),
            'total_payment': data.get('total_payment'),
            'total_adjusted_payout': data.get('total_adjusted_payout'),
            'expense': data.get('expense'),
            'loan': data.get('loan'),
            'advance_salary': data.get('advance_salary'),
            'bonus': data.get('bonus'),
            'status': data.get('status'),
            'updated_on': data.get('updated_on'),
            'created_on': data.get('created_on'),
            'last_updated': data.get('last_updated'),
            'provident_employee': data.get('provident_employee'),
            'provident_employer': data.get('provident_employer'),
            'total_provident': data.get('total_provident')
        }

        return {
            'doc_ids': docs.ids,
            'doc_model': 'custom.hr.payroll.report',
            'docs': docs,
            'datas': data,
            'colum': colum,
        }


