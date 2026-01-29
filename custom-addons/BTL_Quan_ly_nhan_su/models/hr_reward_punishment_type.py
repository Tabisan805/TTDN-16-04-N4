# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrRewardPunishmentType(models.Model):
    _name = 'hr.reward.punishment.type'
    _description = 'Loại thưởng phạt'
    
    name = fields.Char(string='Tên loại', required=True)
    code = fields.Char(string='Mã', required=True)
    type = fields.Selection([
        ('reward', 'Thưởng'),
        ('punishment', 'Phạt'),
    ], string='Phân loại', required=True)
    
    amount_type = fields.Selection([
        ('fixed', 'Cố định'),
        ('percentage', 'Phần trăm lương'),
    ], string='Loại số tiền', default='fixed', required=True)
    
    default_amount = fields.Float(string='Số tiền mặc định')
    active = fields.Boolean(string='Hoạt động', default=True)
    description = fields.Text(string='Mô tả')
    
    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'Mã loại thưởng phạt đã tồn tại!'),
    ]
