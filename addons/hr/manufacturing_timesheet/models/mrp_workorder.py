# -*- coding: utf-8 -*-
################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Cybrosys Technologies(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
from datetime import datetime
from odoo import fields, models


class MrpWorkorder(models.Model):
    """Inherited model mrp_workorder to add field and functions related to
       manufacturing timesheet.

        Methods:
            button_start(self):
                Supering the function of start button to start the time of
                timesheet.
            button_pending(self):
                Supering the function of pause button to set timesheet in
                progress state.
            button_finish(self):
                Supering the function of done button to calculate total
                time in timesheet.
    """
    _inherit = 'mrp.workorder'

    employee_id = fields.Many2one('hr.employee', string='Employee',
                                  readonly=False, required=True,
                                  help='Employee in work order', store=True)

    def button_start(self):
        """ Supering the function of start button to start the timer
            of timesheet.

            Boolean: Returns true
        """
        res = super(MrpWorkorder, self).button_start()
        minutes = int(self.duration_expected)
        seconds = int((self.duration_expected - minutes) * 60)
        time_str = f"{minutes:02d}:{seconds:02d}"
        minutes_str, seconds_str = time_str.split(":")
        minutes = int(minutes_str)
        seconds = int(seconds_str)
        if seconds % 30 == 0:
            minutes += (seconds // 30)
        total_allocated_hours = minutes / 60
        project = self.env['project.project'].search(
            [('name', '=', ("MO: {}".format(self.production_id.name)))])
        if project:
            task_id = project.task_ids.search([('name', '=', (
                "{} in {} for {} on {}".format(self.name,
                                               self.workcenter_id.name,
                                               self.product_id.display_name,
                                               str(self.date_start))))])
            if not task_id:
                task_id = self.env['project.task'].create({
                    'name': ("{} in {} for {} on {}".format(self.name,
                                                            self.workcenter_id.name,
                                                            self.product_id.display_name,
                                                            str(self.date_start))),
                    'project_id': project.id,
                    'date_assign': self.date_start,
                    'date_deadline': self.date_finished,
                    'allocated_hours': total_allocated_hours,
                })
                self.env['account.analytic.line'].create({
                    'task_id': task_id.id,
                    'date': datetime.today(),
                    'name': ("{} in {} for {}".format(self.name,
                                                      self.workcenter_id.name,
                                                      self.product_id.display_name)),
                    'employee_id': self.employee_id.id,
                    'is_manufacturing': True
                })
        else:
            project_id = self.env['project.project'].create(
                {'name': ("MO: {}".format(self.production_id.name)),
                 'is_manufacturing': True})
            task_id = project_id.task_ids.search([('name', '=', (
                "{} in {} for {} on {}".format(self.name,
                                               self.workcenter_id.name,
                                               self.product_id.display_name,
                                               str(self.date_start))))])
            if not task_id:
                task_id = self.env['project.task'].create({
                    'name': ("{} in {} for {} on {}".format(self.name,
                                                            self.workcenter_id.name,
                                                            self.product_id.display_name,
                                                            str(self.date_start))),
                    'project_id': project_id.id,
                    'date_assign': self.date_start,
                    'date_deadline': self.date_finished,
                    'allocated_hours': total_allocated_hours,
                })
                self.env['account.analytic.line'].create({
                    'task_id': task_id.id,
                    'date': datetime.today(),
                    'name': ("{} in {} for {}".format(self.name,
                                                      self.workcenter_id.name,
                                                      self.product_id.display_name)),
                    'employee_id': self.employee_id.id,
                    'is_manufacturing': True
                })
        return res

    def button_pending(self):
        """ Supering the function of pause button to set timesheet in
            progress state.

            Boolean: Returns true
        """
        res = super(MrpWorkorder, self).button_pending()

        allocated_hours = int(self.duration_expected)
        allocated_minutes = int(
            (self.duration_expected - allocated_hours) * 60)
        allocated_time_str = f"{allocated_hours:02d}:{allocated_minutes:02d}"
        allocated_minutes_str, allocated_seconds_str = allocated_time_str.split(
            ":")
        allocated_minutes = int(allocated_minutes_str)
        allocated_seconds = int(allocated_minutes_str)
        total_allocated_hours = (
                            allocated_minutes + allocated_seconds / 60) / 60
        project = self.env['project.project'].search(
            [('name', '=', ("MO: {}".format(self.production_id.name)))])
        task_id = project.task_ids.search([('name', '=', (
            "{} in {} for {} on {}".format(self.name, self.workcenter_id.name,
                                           self.product_id.display_name,
                                           str(self.date_start))))])
        task_id.write({
            'allocated_hours': total_allocated_hours
        })
        timesheet = task_id.mapped('timesheet_ids')
        hours = int(self.duration)
        minutes = int((self.duration - hours) * 60)
        time_str = f"{hours:02d}:{minutes:02d}"
        minutes_str, seconds_str = time_str.split(":")
        minutes = int(minutes_str)
        seconds = int(seconds_str)
        total_hours = (minutes + seconds / 60) / 60
        for rec in timesheet:
            rec.write({
                'unit_amount': total_hours,
            })
        return res

    def button_finish(self):
        """ Supering the function of done button to calculate total time in
            timesheet.

            Boolean: Returns true
        """
        res = super(MrpWorkorder, self).button_finish()

        allocated_hours = int(self.duration_expected)
        allocated_minutes = int(
            (self.duration_expected - allocated_hours) * 60)
        allocated_time_str = f"{allocated_hours:02d}:{allocated_minutes:02d}"
        allocated_minutes_str, allocated_seconds_str = allocated_time_str.split(
            ":")
        allocated_minutes = int(allocated_minutes_str)
        allocated_seconds = int(allocated_minutes_str)
        total_allocated_hours = (
                            allocated_minutes + allocated_seconds / 60) / 60
        project = self.env['project.project'].search(
            [('name', '=', ("MO: {}".format(self.production_id.name)))])
        task_id = project.task_ids.search([('name', '=', (
            "{} in {} for {} on {}".format(self.name, self.workcenter_id.name,
                                           self.product_id.display_name,
                                           str(self.date_start))))])
        task_id.write({
            'allocated_hours': total_allocated_hours
        })
        timesheet = task_id.mapped('timesheet_ids')
        hours = int(self.duration)
        minutes = int((self.duration - hours) * 60)
        time_str = f"{hours:02d}:{minutes:02d}"
        minutes_str, seconds_str = time_str.split(":")
        minutes = int(minutes_str)
        seconds = int(seconds_str)
        total_hours = (minutes + seconds / 60) / 60
        for rec in timesheet:
            rec.write({
                'unit_amount': total_hours,
            })
        return res
