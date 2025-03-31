from odoo import models, fields, api

class HREmployee(models.Model):
    _inherit = "hr.employee"

    @api.model
    def get_hr_metrics_chart(self):
        """Returns data formatted for Chart.js for various HR metrics."""
        
        # Contract Running vs Exit
        query_contracts = """
            SELECT state, COUNT(*)
            FROM hr_contract
            GROUP BY state
        """
        self._cr.execute(query_contracts)
        results_contracts = self._cr.fetchall()
        contract_labels = ["Running", "Exit"]
        contract_data = [0, 0]
        for state, count in results_contracts:
            if state == 'open':
                contract_data[0] = count
            elif state == 'close':
                contract_data[1] = count

        # Turnover Rate
        query_turnover = """
            SELECT COUNT(*)
            FROM hr_employee
            WHERE active = False
        """
        self._cr.execute(query_turnover)
        turnover_count = self._cr.fetchone()[0]

        query_total_employees = """
            SELECT COUNT(*)
            FROM hr_employee
            WHERE active = True
        """
        self._cr.execute(query_total_employees)
        total_employees = self._cr.fetchone()[0]

        turnover_rate = (turnover_count / total_employees) * 100 if total_employees > 0 else 0

        # Absent Rate
        query_absent = """
            SELECT COUNT(*)
            FROM hr_leave
            WHERE state = 'validate'
        """
        self._cr.execute(query_absent)
        absent_count = self._cr.fetchone()[0]

        absent_rate = (absent_count / total_employees) * 100 if total_employees > 0 else 0

        # Pending Leaves
        query_pending_leaves = """
            SELECT COUNT(*)
            FROM hr_leave
            WHERE state = 'confirm'
        """
        self._cr.execute(query_pending_leaves)
        pending_leaves = self._cr.fetchone()[0]

        # Contract Expiration Dates
        query_contract_expiration = """
            SELECT date_end, COUNT(*)
            FROM hr_contract
            WHERE date_end IS NOT NULL
            GROUP BY date_end
            ORDER BY date_end
        """
        self._cr.execute(query_contract_expiration)
        results_contract_expiration = self._cr.fetchall()
        contract_expiration_labels = [str(rec[0]) for rec in results_contract_expiration]
        contract_expiration_data = [rec[1] for rec in results_contract_expiration]

        # Total Jobs
        query_total_jobs = """
            SELECT COUNT(*) FROM hr_job
        """
        self._cr.execute(query_total_jobs)
        total_jobs = self._cr.fetchone()[0]

        # Total Leaves
        query_total_leaves = """
            SELECT COUNT(*) FROM hr_leave
        """
        self._cr.execute(query_total_leaves)
        total_leaves = self._cr.fetchone()[0]

        # Total Departments
        query_total_departments = """
            SELECT COUNT(*) FROM hr_department
        """
        self._cr.execute(query_total_departments)
        total_departments = self._cr.fetchone()[0]

        # Total Active Employees with Running Contracts
        query_active_employees_with_contract = """
            SELECT COUNT(*)
            FROM hr_employee e
            JOIN hr_contract c ON e.id = c.employee_id
            WHERE e.active = True AND c.state = 'open'
        """
        self._cr.execute(query_active_employees_with_contract)
        total_active_employees_with_contract = self._cr.fetchone()[0]

        return {
            "contract_running_vs_exit": {
                "labels": contract_labels,
                "data": contract_data,
            },
            "turnover_rate": turnover_rate,
            "absent_rate": absent_rate,
            "pending_leaves": pending_leaves,
            "contract_expiration": {
                "labels": contract_expiration_labels,
                "data": contract_expiration_data,
            },
            "total_jobs": total_jobs,
            "total_leaves": total_leaves,
            "total_departments": total_departments,
            "total_active_employees_with_running_contract": total_active_employees_with_contract,
        }
