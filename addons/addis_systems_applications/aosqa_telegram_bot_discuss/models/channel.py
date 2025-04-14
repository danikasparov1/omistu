# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo import osv
from odoo.exceptions import UserError


class TelegramChannel(models.Model):
    _name = 'telegram.channel'
    description = 'Telegram Channe'
    name = fields.Char('Name')
    channel_id = fields.Char(string="Channel Id")
    
class AccountAccountTag(models.Model):
    _name = 'telegram.channel.discuss'
    _description = 'Telegram Channel with Odoo Channel'
    name = fields.Char('Name')
    telegram_channel=fields.Many2one('telegram.channel',ondelete='cascade')
    odoo_disccuss = fields.Many2one('discuss.channel',ondelete='cascade')
