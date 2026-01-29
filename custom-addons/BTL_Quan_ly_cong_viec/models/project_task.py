# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class ProjectTask(models.Model):
    """Quản lý công việc BTL - Kế thừa từ project.task"""
    _inherit = 'project.task'
    
    # ==================== THÔNG TIN CƠ BẢN ====================
    
    # Phòng ban và phân loại
    department_id = fields.Many2one(
        'hr.department', 
        string='Phòng ban', 
        tracking=True
    )
    task_type_code = fields.Selection([
        ('sale', 'Sale - Bán hàng'),
        ('marketing', 'Marketing'),
        ('accounting', 'Kế toán'),
        ('hr', 'Nhân sự'),
        ('assistant', 'Trợ lý'),
    ], string='Loại công việc', required=True, tracking=True, default='sale')
    
    # ==================== LIÊN KẾT NGHIỆP VỤ ====================
    
    partner_id = fields.Many2one(
        'res.partner', 
        string='Khách hàng', 
        tracking=True,
        help='Khách hàng liên quan đến công việc này'
    )
    lead_id = fields.Many2one(
        'crm.lead', 
        string='Lead/Cơ hội', 
        tracking=True,
        help='Lead hoặc cơ hội bán hàng liên quan'
    )
    sale_order_id = fields.Many2one(
        'sale.order', 
        string='Đơn hàng', 
        tracking=True,
        help='Đơn hàng liên quan đến công việc'
    )
    
    # ==================== PHÂN CÔNG ====================
    
    assigned_by_id = fields.Many2one(
        'res.users', 
        string='Người giao việc', 
        default=lambda self: self.env.user, 
        tracking=True,
        help='Người giao/tạo công việc này'
    )
    collaborator_ids = fields.Many2many(
        'res.users', 
        'task_collaborator_rel', 
        'task_id', 
        'user_id', 
        string='Người phối hợp',
        help='Các nhân viên hỗ trợ thực hiện công việc'
    )
    
    # ==================== ƯU TIÊN ====================
    
    priority_level = fields.Selection([
        ('low', 'Thấp'),
        ('normal', 'Bình thường'),
        ('high', 'Cao'),
        ('urgent', 'Khẩn cấp'),
    ], string='Mức độ ưu tiên', default='normal', required=True, tracking=True)
    
    # ==================== THỜI GIAN ====================
    
    date_start = fields.Datetime(
        string='Thời gian bắt đầu', 
        tracking=True
    )
    date_end = fields.Datetime(
        string='Thời gian kết thúc thực tế', 
        tracking=True,
        help='Thời gian hoàn thành thực tế'
    )
    duration_planned = fields.Float(
        string='Thời gian dự kiến (giờ)', 
        compute='_compute_duration_planned', 
        store=True,
        help='Tự động tính từ ngày bắt đầu đến deadline'
    )
    duration_actual = fields.Float(
        string='Thời gian thực tế (giờ)', 
        compute='_compute_duration_actual', 
        store=True,
        help='Tự động tính từ ngày bắt đầu đến ngày kết thúc thực tế'
    )
    is_overdue = fields.Boolean(
        string='Quá hạn', 
        compute='_compute_is_overdue', 
        store=True, 
        tracking=True
    )
    
    # ==================== TRẠNG THÁI ====================
    
    task_status = fields.Selection([
        ('not_started', 'Chưa bắt đầu'),
        ('in_progress', 'Đang thực hiện'),
        ('waiting', 'Chờ phản hồi'),
        ('on_hold', 'Tạm dừng'),
        ('completed', 'Hoàn thành'),
        ('cancelled', 'Đã hủy'),
    ], string='Trạng thái', default='not_started', required=True, tracking=True)
    
    # ==================== KẾT QUẢ ====================
    
    result_note = fields.Text(
        string='Kết quả thực hiện',
        help='Mô tả chi tiết kết quả và sản phẩm đầu ra của công việc'
    )
    completion_percentage = fields.Float(
        string='Tỷ lệ hoàn thành (%)', 
        default=0.0, 
        tracking=True,
        help='Tiến độ hoàn thành công việc từ 0-100%'
    )
    
    # ==================== BÀN GIAO ====================
    
    handover_ids = fields.One2many(
        'task.handover.btl', 
        'task_id', 
        string='Lịch sử bàn giao'
    )
    handover_count = fields.Integer(
        string='Số lần bàn giao', 
        compute='_compute_handover_count'
    )
    
    # ==================== LỊCH SỬ ====================
    
    history_ids = fields.One2many(
        'task.history.btl', 
        'task_id', 
        string='Lịch sử thay đổi'
    )
    history_count = fields.Integer(
        string='Số thay đổi', 
        compute='_compute_history_count'
    )
    
    # ==================== THỐNG KÊ ====================
    
    total_time_spent = fields.Float(
        string='Tổng thời gian (giờ)', 
        help='Tổng thời gian đã làm việc (giờ)'
    )
    
    # ==================== COMPUTED FIELDS ====================
    
    @api.depends('date_start', 'date_deadline')
    def _compute_duration_planned(self):
        """Tính thời gian dự kiến"""
        for task in self:
            if task.date_start and task.date_deadline:
                start = fields.Datetime.to_datetime(task.date_start)
                deadline = datetime.combine(task.date_deadline, datetime.max.time())
                delta = deadline - start
                task.duration_planned = delta.total_seconds() / 3600.0
            else:
                task.duration_planned = 0.0
    
    @api.depends('date_start', 'date_end')
    def _compute_duration_actual(self):
        """Tính thời gian thực tế"""
        for task in self:
            if task.date_start and task.date_end:
                delta = task.date_end - task.date_start
                task.duration_actual = delta.total_seconds() / 3600.0
            else:
                task.duration_actual = 0.0
    
    @api.depends('date_deadline', 'task_status')
    def _compute_is_overdue(self):
        """Kiểm tra công việc quá hạn"""
        today = fields.Date.today()
        for task in self:
            if task.date_deadline and task.task_status not in ['completed', 'cancelled']:
                # Convert date_deadline to date for comparison
                deadline_date = task.date_deadline.date() if isinstance(task.date_deadline, datetime) else task.date_deadline
                task.is_overdue = deadline_date < today
            else:
                task.is_overdue = False
    
    @api.depends('handover_ids')
    def _compute_handover_count(self):
        """Đếm số lần bàn giao"""
        for task in self:
            task.handover_count = len(task.handover_ids)
    
    @api.depends('history_ids')
    def _compute_history_count(self):
        """Đếm số lần thay đổi"""
        for task in self:
            task.history_count = len(task.history_ids)
    
    # ==================== CONSTRAINTS ====================
    
    @api.constrains('completion_percentage')
    def _check_completion_percentage(self):
        """Kiểm tra tỷ lệ hoàn thành"""
        for task in self:
            if not (0 <= task.completion_percentage <= 100):
                raise ValidationError(_('Tỷ lệ hoàn thành phải từ 0 đến 100%!'))
    
    @api.constrains('date_start', 'date_deadline')
    def _check_dates(self):
        """Kiểm tra logic thời gian"""
        for task in self:
            if task.date_start and task.date_deadline:
                start_date = task.date_start.date() if isinstance(task.date_start, datetime) else task.date_start
                if start_date > task.date_deadline:
                    raise ValidationError(_('Thời gian bắt đầu không thể sau thời gian kết thúc!'))
    
    # ==================== ACTIONS ====================
    
    def action_start_task(self):
        """Bắt đầu công việc"""
        for task in self:
            if task.task_status == 'not_started':
                task.write({
                    'task_status': 'in_progress',
                    'date_start': fields.Datetime.now(),
                })
                task._create_history('Bắt đầu thực hiện công việc')
        return True
    
    def action_complete_task(self):
        """Hoàn thành công việc"""
        for task in self:
            if task.task_status != 'completed':
                task.write({
                    'task_status': 'completed',
                    'date_end': fields.Datetime.now(),
                    'completion_percentage': 100.0,
                })
                task._create_history('Hoàn thành công việc')
        return True
    
    def action_cancel_task(self):
        """Hủy công việc"""
        for task in self:
            if task.task_status not in ['completed', 'cancelled']:
                task.write({
                    'task_status': 'cancelled',
                    'date_end': fields.Datetime.now(),
                })
                task._create_history('Hủy công việc')
        return True
    
    def action_handover_task(self):
        """Mở wizard bàn giao công việc"""
        self.ensure_one()
        return {
            'name': _('Bàn giao công việc'),
            'type': 'ir.actions.act_window',
            'res_model': 'task.handover.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_task_id': self.id,
                'default_from_user_id': self.user_ids[0].id if self.user_ids else self.env.user.id,
            }
        }
    
    def action_view_handover_history(self):
        """Xem lịch sử bàn giao"""
        self.ensure_one()
        return {
            'name': _('Lịch sử bàn giao'),
            'type': 'ir.actions.act_window',
            'res_model': 'task.handover.btl',
            'view_mode': 'tree,form',
            'domain': [('task_id', '=', self.id)],
            'context': {'default_task_id': self.id}
        }
    
    def action_view_change_history(self):
        """Xem lịch sử thay đổi"""
        self.ensure_one()
        return {
            'name': _('Lịch sử thay đổi'),
            'type': 'ir.actions.act_window',
            'res_model': 'task.history.btl',
            'view_mode': 'tree,form',
            'domain': [('task_id', '=', self.id)],
            'context': {'default_task_id': self.id}
        }
    
    # ==================== HELPERS ====================
    
    def _create_history(self, description, old_value='', new_value=''):
        """Tạo bản ghi lịch sử thay đổi"""
        self.ensure_one()
        self.env['task.history.btl'].create({
            'task_id': self.id,
            'user_id': self.env.user.id,
            'change_date': fields.Datetime.now(),
            'description': description,
            'old_value': old_value,
            'new_value': new_value,
        })
    
    # ==================== OVERRIDE ====================
    
    @api.model_create_multi
    def create(self, vals_list):
        """Override create để tự động ghi nhận lịch sử"""
        tasks = super(ProjectTask, self).create(vals_list)
        for task in tasks:
            task._create_history('Tạo mới công việc')
        return tasks
    
    def write(self, vals):
        """Override write để tự động ghi nhận lịch sử thay đổi"""
        # Lưu trạng thái cũ để tracking
        for task in self:
            # Tracking status changes
            if 'task_status' in vals and vals['task_status'] != task.task_status:
                old_status = dict(task._fields['task_status'].selection).get(task.task_status)
                new_status = dict(task._fields['task_status'].selection).get(vals['task_status'])
                task._create_history(
                    f'Thay đổi trạng thái',
                    old_value=old_status,
                    new_value=new_status
                )
            
            # Tracking priority changes
            if 'priority_level' in vals and vals['priority_level'] != task.priority_level:
                old_priority = dict(task._fields['priority_level'].selection).get(task.priority_level)
                new_priority = dict(task._fields['priority_level'].selection).get(vals['priority_level'])
                task._create_history(
                    f'Thay đổi mức độ ưu tiên',
                    old_value=old_priority,
                    new_value=new_priority
                )
            
            # Tracking assignee changes
            if 'user_ids' in vals:
                old_users = ', '.join(task.user_ids.mapped('name'))
                task._create_history(
                    f'Thay đổi người thực hiện',
                    old_value=old_users
                )
            
            # Tracking completion percentage
            if 'completion_percentage' in vals and vals['completion_percentage'] != task.completion_percentage:
                task._create_history(
                    f'Cập nhật tiến độ',
                    old_value=f'{task.completion_percentage}%',
                    new_value=f"{vals['completion_percentage']}%"
                )
        
        return super(ProjectTask, self).write(vals)
