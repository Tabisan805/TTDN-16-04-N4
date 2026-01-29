# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CrmInteractionType(models.Model):
    _name = 'crm.interaction.type'
    _description = 'Loại tương tác khách hàng'
    _order = 'sequence, name'
    
    name = fields.Char(string='Tên loại tương tác', required=True)
    code = fields.Char(string='Mã', required=True)
    sequence = fields.Integer(string='Thứ tự', default=10)
    active = fields.Boolean(string='Hoạt động', default=True)
    icon = fields.Char(string='Icon', help='Font Awesome icon class')
    color = fields.Integer(string='Màu sắc')
    
    description = fields.Text(string='Mô tả')
    
    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'Mã loại tương tác đã tồn tại!'),
    ]
