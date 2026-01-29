# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class TaskHandover(models.Model):
    """Quản lý bàn giao công việc"""
    _name = 'task.handover.btl'
    _description = 'Bàn giao công việc BTL'
    _order = 'handover_date desc'
    
    task_id = fields.Many2one(
        'project.task', 
        string='Công việc', 
        required=True, 
        ondelete='cascade'
    )
    from_user_id = fields.Many2one(
        'res.users', 
        string='Người bàn giao', 
        required=True,
        help='Người bàn giao công việc'
    )
    to_user_id = fields.Many2one(
        'res.users', 
        string='Người nhận', 
        required=True,
        help='Người nhận bàn giao công việc'
    )
    handover_date = fields.Datetime(
        string='Thời gian bàn giao', 
        default=fields.Datetime.now, 
        required=True
    )
    reason = fields.Text(
        string='Lý do bàn giao', 
        required=True,
        help='Mô tả lý do tại sao bàn giao công việc này'
    )
    note = fields.Text(
        string='Ghi chú',
        help='Ghi chú thêm về quá trình bàn giao'
    )
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('confirmed', 'Đã xác nhận'),
        ('rejected', 'Từ chối'),
    ], string='Trạng thái', default='draft', tracking=True)
    
    # Thông tin công việc tại thời điểm bàn giao
    task_status_at_handover = fields.Char(
        string='Trạng thái công việc',
        help='Trạng thái công việc tại thời điểm bàn giao'
    )
    completion_at_handover = fields.Float(
        string='Tiến độ (%)',
        help='Tiến độ hoàn thành tại thời điểm bàn giao'
    )
    
    def action_confirm(self):
        """Xác nhận bàn giao"""
        for record in self:
            if record.state == 'draft':
                # Cập nhật người thực hiện trong task
                record.task_id.write({
                    'user_ids': [(6, 0, [record.to_user_id.id])]
                })
                record.write({'state': 'confirmed'})
                # Tạo lịch sử
                record.task_id._create_history(
                    f'Bàn giao công việc từ {record.from_user_id.name} sang {record.to_user_id.name}',
                    old_value=record.from_user_id.name,
                    new_value=record.to_user_id.name
                )
        return True
    
    def action_reject(self):
        """Từ chối bàn giao"""
        for record in self:
            if record.state == 'draft':
                record.write({'state': 'rejected'})
        return True
