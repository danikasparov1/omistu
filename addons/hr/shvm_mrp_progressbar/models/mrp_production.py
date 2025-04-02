# -*- coding: utf-8 -*-
# Email: sales@creyox.com

from odoo import models, fields, api, _


class MrpWorkOrder(models.Model):
    _inherit = 'mrp.workorder'

    is_completed = fields.Boolean()


class ResCompany(models.Model):
    _inherit = 'mrp.production'

    mrp_progress = fields.Float(compute='compute_mo_progress')

    @api.depends('workorder_ids.duration_expected', 'workorder_ids.duration')
    def compute_mo_progress(self):
        self.mrp_progress = 0.0
        for mo in self:
            expected_duration = 0
            real_duration = 0
            progress = 0
            total_wo = 0
            completed_wo = 0
            if mo.workorder_ids:
                for wo in mo.workorder_ids:
                    total_wo += 1
                    if not wo.is_completed:
                        expected_duration += wo.duration_expected
                        real_duration += wo.duration
                    else:
                        expected_duration += wo.duration_expected
                        real_duration += wo.duration_expected
                        # completed_wo += 1
                if expected_duration != 0 and real_duration != 0:
                    progress = (real_duration * 100) / expected_duration
                    if progress > 100:
                        mo.mrp_progress = 100
                    else:
                        mo.mrp_progress = progress
            else:
                mo.mrp_progress = 0.0
