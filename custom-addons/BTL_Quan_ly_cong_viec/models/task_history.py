# -*- coding: utf-8 -*-

from odoo import models, fields


class TaskHistory(models.Model):
    """Lịch sử thay đổi công việc"""
    _name = 'task.history.btl'
    _description = 'Lịch sử thay đổi công việc BTL'
    _order = 'change_date desc'
    
    task_id = fields.Many2one(
        'project.task', 
        string='Công việc', 
        required=True, 
        ondelete='cascade',
        index=True
    )
    user_id = fields.Many2one(
        'res.users', 
        string='Người thực hiện', 
        required=True,
        default=lambda self: self.env.user,
        help='Người thực hiện thay đổi'
    )
    change_date = fields.Datetime(
        string='Thời gian', 
        default=fields.Datetime.now, 
        required=True,
        help='Thời gian thay đổi'
    )
    description = fields.Char(
        string='Mô tả', 
        required=True,
        help='Mô tả ngắn gọn về thay đổi'
    )
    old_value = fields.Text(
        string='Giá trị cũ',
        help='Giá trị trước khi thay đổi'
    )
    new_value = fields.Text(
        string='Giá trị mới',
        help='Giá trị sau khi thay đổi'
    )
    change_type = fields.Selection([
        ('create', 'Tạo mới'),
        ('status', 'Thay đổi trạng thái'),
        ('assign', 'Phân công'),
        ('priority', 'Ưu tiên'),
        ('progress', 'Tiến độ'),
        ('handover', 'Bàn giao'),
        ('other', 'Khác'),
    ], string='Loại thay đổi', default='other')
