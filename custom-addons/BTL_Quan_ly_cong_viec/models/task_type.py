# -*- coding: utf-8 -*-

from odoo import models, fields, api


class TaskType(models.Model):
    """Loại công việc BTL"""
    _name = 'task.type.btl'
    _description = 'Loại công việc BTL'
    _order = 'sequence, name'
    
    name = fields.Char(string='Tên loại công việc', required=True, translate=True)
    code = fields.Selection([
        ('sale', 'Sale - Bán hàng'),
        ('marketing', 'Marketing'),
        ('accounting', 'Kế toán'),
        ('hr', 'Nhân sự'),
        ('assistant', 'Trợ lý'),
    ], string='Mã loại', required=True)
    description = fields.Text(string='Mô tả')
    sequence = fields.Integer(string='Thứ tự', default=10)
    
    # Phòng ban áp dụng
    department_ids = fields.Many2many('hr.department', string='Phòng ban áp dụng')
    
    # Cấu hình
    color = fields.Integer(string='Màu sắc')
    icon = fields.Char(string='Icon')
    active = fields.Boolean(string='Hoạt động', default=True)
    
    # Thống kê
    task_count = fields.Integer(string='Số công việc', compute='_compute_task_count')
    
    @api.depends('code')
    def _compute_task_count(self):
        for record in self:
            record.task_count = self.env['project.task'].search_count([
                ('task_type_code', '=', record.code)
            ])
    
    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'Mã loại công việc đã tồn tại!'),
    ]
