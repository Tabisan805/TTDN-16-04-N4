# -*- coding: utf-8 -*-

from odoo import models, fields, api


class TaskPerformance(models.Model):
    """Báo cáo hiệu suất công việc"""
    _name = 'task.performance.btl'
    _description = 'Hiệu suất công việc BTL'
    _order = 'period_start desc'
    
    name = fields.Char(
        string='Tên báo cáo', 
        compute='_compute_name', 
        store=True
    )
    user_id = fields.Many2one(
        'res.users', 
        string='Nhân viên', 
        required=True,
        help='Nhân viên được đánh giá'
    )
    department_id = fields.Many2one(
        'hr.department', 
        string='Phòng ban',
        related='user_id.employee_id.department_id',
        store=True
    )
    period_start = fields.Date(
        string='Từ ngày', 
        required=True
    )
    period_end = fields.Date(
        string='Đến ngày', 
        required=True
    )
    
    # Thống kê công việc
    total_tasks = fields.Integer(
        string='Tổng công việc', 
        compute='_compute_statistics', 
        store=True
    )
    completed_tasks = fields.Integer(
        string='Hoàn thành', 
        compute='_compute_statistics', 
        store=True
    )
    in_progress_tasks = fields.Integer(
        string='Đang thực hiện', 
        compute='_compute_statistics', 
        store=True
    )
    overdue_tasks = fields.Integer(
        string='Quá hạn', 
        compute='_compute_statistics', 
        store=True
    )
    cancelled_tasks = fields.Integer(
        string='Đã hủy', 
        compute='_compute_statistics', 
        store=True
    )
    
    # Tỷ lệ
    completion_rate = fields.Float(
        string='Tỷ lệ hoàn thành (%)', 
        compute='_compute_rates', 
        store=True
    )
    ontime_rate = fields.Float(
        string='Tỷ lệ đúng hạn (%)', 
        compute='_compute_rates', 
        store=True
    )
    
    # Thời gian
    avg_completion_time = fields.Float(
        string='Thời gian TB (giờ)', 
        compute='_compute_statistics', 
        store=True,
        help='Thời gian hoàn thành trung bình'
    )
    
    # Điểm hiệu suất
    performance_score = fields.Float(
        string='Điểm hiệu suất', 
        compute='_compute_performance_score', 
        store=True,
        help='Điểm hiệu suất tổng hợp (0-100)'
    )
    
    @api.depends('user_id', 'period_start', 'period_end')
    def _compute_name(self):
        for record in self:
            if record.user_id and record.period_start and record.period_end:
                record.name = f'Hiệu suất {record.user_id.name} ({record.period_start} - {record.period_end})'
            else:
                record.name = 'Báo cáo hiệu suất'
    
    @api.depends('user_id', 'period_start', 'period_end')
    def _compute_statistics(self):
        """Tính toán thống kê công việc"""
        for record in self:
            if not record.user_id or not record.period_start or not record.period_end:
                record.total_tasks = 0
                record.completed_tasks = 0
                record.in_progress_tasks = 0
                record.overdue_tasks = 0
                record.cancelled_tasks = 0
                record.avg_completion_time = 0.0
                continue
            
            domain = [
                ('user_ids', 'in', record.user_id.ids),
                ('date_start', '>=', record.period_start),
                ('date_start', '<=', record.period_end),
            ]
            
            tasks = self.env['project.task'].search(domain)
            record.total_tasks = len(tasks)
            record.completed_tasks = len(tasks.filtered(lambda t: t.task_status == 'completed'))
            record.in_progress_tasks = len(tasks.filtered(lambda t: t.task_status == 'in_progress'))
            record.overdue_tasks = len(tasks.filtered(lambda t: t.is_overdue))
            record.cancelled_tasks = len(tasks.filtered(lambda t: t.task_status == 'cancelled'))
            
            # Tính thời gian hoàn thành trung bình
            completed = tasks.filtered(lambda t: t.task_status == 'completed' and t.duration_actual > 0)
            if completed:
                record.avg_completion_time = sum(completed.mapped('duration_actual')) / len(completed)
            else:
                record.avg_completion_time = 0.0
    
    @api.depends('total_tasks', 'completed_tasks', 'overdue_tasks')
    def _compute_rates(self):
        """Tính tỷ lệ hoàn thành"""
        for record in self:
            if record.total_tasks > 0:
                record.completion_rate = (record.completed_tasks / record.total_tasks) * 100
                ontime = record.completed_tasks - record.overdue_tasks
                record.ontime_rate = (ontime / record.total_tasks) * 100 if ontime > 0 else 0.0
            else:
                record.completion_rate = 0.0
                record.ontime_rate = 0.0
    
    @api.depends('completion_rate', 'ontime_rate', 'overdue_tasks', 'total_tasks')
    def _compute_performance_score(self):
        """Tính điểm hiệu suất tổng hợp"""
        for record in self:
            if record.total_tasks == 0:
                record.performance_score = 0.0
                continue
            
            # Công thức: 
            # - 50% từ tỷ lệ hoàn thành
            # - 30% từ tỷ lệ đúng hạn
            # - 20% trừ điểm từ công việc quá hạn
            score = (record.completion_rate * 0.5) + (record.ontime_rate * 0.3)
            
            # Trừ điểm nếu có công việc quá hạn
            overdue_penalty = (record.overdue_tasks / record.total_tasks) * 20
            score -= overdue_penalty
            
            record.performance_score = max(0, min(100, score))
