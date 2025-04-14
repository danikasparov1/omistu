from odoo import models, fields, api, exceptions


class StockMove(models.Model):
    _inherit = 'stock.move'

    quality_check_id = fields.Many2one('quality.check', string='Quality Check')
    
    
    

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    quality_check_id = fields.Many2one('quality.check', string='Quality Check')