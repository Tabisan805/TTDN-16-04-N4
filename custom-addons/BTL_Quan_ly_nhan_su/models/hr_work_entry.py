# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta


class HrWorkEntry(models.Model):
    _name = 'hr.work.entry.btl'
    _description = 'Bảng công'
    _order = 'date desc'
    
    employee_id = fields.Many2one('hr.employee', string='Nhân viên', required=True, ondelete='cascade')
    department_id = fields.Many2one('hr.department', string='Phòng ban', related='employee_id.department_id', store=True)
    
    # Kỳ tính công
    date = fields.Date(string='Tháng', required=True, default=fields.Date.today)
    date_from = fields.Date(string='Từ ngày', compute='_compute_period', store=True)
    date_to = fields.Date(string='Đến ngày', compute='_compute_period', store=True)
    
    # Ngày công
    total_work_days = fields.Float(string='Tổng ngày công', compute='_compute_work_summary', store=True)
    standard_work_days = fields.Float(string='Ngày công chuẩn', related='employee_id.standard_working_days')
    
    # Thời gian
    total_worked_hours = fields.Float(string='Tổng giờ làm', compute='_compute_work_summary', store=True)
    total_overtime = fields.Float(string='Tổng giờ tăng ca', compute='_compute_work_summary', store=True)
    
    # Đi trễ, về sớm
    total_late_times = fields.Integer(string='Số lần đi trễ', compute='_compute_work_summary', store=True)
    total_early_times = fields.Integer(string='Số lần về sớm', compute='_compute_work_summary', store=True)
    
    # Nghỉ phép
    total_leave_days = fields.Float(string='Số ngày nghỉ phép', compute='_compute_work_summary', store=True)
    total_unpaid_leave_days = fields.Float(string='Ngày nghỉ không lương', compute='_compute_work_summary', store=True)
    
    # Chi tiết
    attendance_ids = fields.One2many('hr.attendance.btl', 'employee_id', string='Chi tiết chấm công',
                                    domain=lambda self: [('date', '>=', self.date_from), ('date', '<=', self.date_to)])
    leave_ids = fields.One2many('hr.leave.btl', 'employee_id', string='Chi tiết nghỉ phép',
                               domain=lambda self: [('date_from', '>=', self.date_from), ('date_to', '<=', self.date_to)])
    overtime_ids = fields.One2many('hr.overtime', 'employee_id', string='Chi tiết tăng ca',
                                  domain=lambda self: [('date', '>=', self.date_from), ('date', '<=', self.date_to)])
    
    # Trạng thái
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('confirmed', 'Đã xác nhận'),
        ('locked', 'Đã khóa'),
    ], string='Trạng thái', default='draft', required=True)
    
    note = fields.Text(string='Ghi chú')
    
    @api.depends('date')
    def _compute_period(self):
        for record in self:
            if record.date:
                record.date_from = record.date.replace(day=1)
                record.date_to = record.date_from + relativedelta(months=1, days=-1)
            else:
                record.date_from = False
                record.date_to = False
    
    @api.depends('date_from', 'date_to', 'employee_id')
    def _compute_work_summary(self):
        for record in self:
            if not record.date_from or not record.date_to or not record.employee_id:
                record.total_work_days = 0
                record.total_worked_hours = 0
                record.total_overtime = 0
                record.total_late_times = 0
                record.total_early_times = 0
                record.total_leave_days = 0
                record.total_unpaid_leave_days = 0
                continue
            
            # Tính tổng từ chấm công
            attendances = self.env['hr.attendance.btl'].search([
                ('employee_id', '=', record.employee_id.id),
                ('date', '>=', record.date_from),
                ('date', '<=', record.date_to),
                ('state', '=', 'validated'),
            ])
            
            record.total_work_days = sum(attendances.mapped('work_days'))
            record.total_worked_hours = sum(attendances.mapped('worked_hours'))
            record.total_late_times = len(attendances.filtered(lambda a: a.is_late))
            record.total_early_times = len(attendances.filtered(lambda a: a.is_early_leave))
            
            # Tính tổng tăng ca
            overtimes = self.env['hr.overtime'].search([
                ('employee_id', '=', record.employee_id.id),
                ('date', '>=', record.date_from),
                ('date', '<=', record.date_to),
                ('state', '=', 'approved'),
            ])
            record.total_overtime = sum(overtimes.mapped('hours'))
            
            # Tính tổng nghỉ phép
            leaves = self.env['hr.leave.btl'].search([
                ('employee_id', '=', record.employee_id.id),
                ('date_from', '>=', record.date_from),
                ('date_to', '<=', record.date_to),
                ('state', '=', 'approved'),
            ])
            record.total_leave_days = sum(leaves.filtered(lambda l: l.is_paid).mapped('number_of_days'))
            record.total_unpaid_leave_days = sum(leaves.filtered(lambda l: not l.is_paid).mapped('number_of_days'))
    
    def action_confirm(self):
        self.write({'state': 'confirmed'})
    
    def action_lock(self):
        """Khóa bảng công và tạo thưởng chuyên cần tự động"""
        self.write({'state': 'locked'})
        self._create_perfect_attendance_bonus()
    
    def _create_perfect_attendance_bonus(self):
        """Tạo thưởng chuyên cần nếu không đi trễ/về sớm"""
        for record in self:
            # Lấy attendance rule
            rule = self.env['hr.attendance.rule'].search([('active', '=', True)], limit=1)
            if not rule or rule.perfect_attendance_bonus <= 0:
                continue
            
            # Kiểm tra điều kiện: Không đi trễ và không về sớm
            if record.total_late_times == 0 and record.total_early_times == 0 and record.total_work_days >= record.standard_work_days:
                # Tìm loại thưởng chuyên cần
                reward_type = self.env['hr.reward.punishment.type'].search([
                    ('code', '=', 'PERFECT_ATTENDANCE'),
                    ('type', '=', 'reward'),
                ], limit=1)
                
                if not reward_type:
                    # Tạo loại thưởng mới nếu chưa có
                    reward_type = self.env['hr.reward.punishment.type'].create({
                        'name': 'Thưởng chuyên cần',
                        'code': 'PERFECT_ATTENDANCE',
                        'type': 'reward',
                        'amount_type': 'fixed',
                        'default_amount': rule.perfect_attendance_bonus,
                    })
                
                # Tạo thưởng
                self.env['hr.reward.punishment'].create({
                    'employee_id': record.employee_id.id,
                    'type_id': reward_type.id,
                    'type': 'reward',
                    'date': record.date,
                    'period': f'{record.date.strftime("%m/%Y")}',
                    'amount': rule.perfect_attendance_bonus,
                    'reason': f'Thưởng chuyên cần tháng {record.date.strftime("%m/%Y")} - Đủ công, không trễ/sớm',
                    'state': 'confirmed',
                })
    
    def action_unlock(self):
        self.write({'state': 'confirmed'})
    
    def action_draft(self):
        self.write({'state': 'draft'})
    
    @api.model
    def _cron_create_monthly_work_entry(self):
        """Tạo bảng công tự động cho tất cả nhân viên vào đầu tháng"""
        today = fields.Date.today()
        
        # Chỉ chạy vào ngày 1 hàng tháng
        if today.day != 1:
            return
        
        # Lấy tất cả nhân viên đang làm việc
        employees = self.env['hr.employee'].search([('status', '=', 'working')])
        
        for employee in employees:
            # Kiểm tra đã có bảng công chưa
            existing = self.search([
                ('employee_id', '=', employee.id),
                ('date', '=', today),
            ])
            
            if not existing:
                self.create({
                    'employee_id': employee.id,
                    'date': today,
                })
    
    @api.model
    def _cron_remind_lock_work_entry(self):
        """Nhắc nhở HR chốt công cuối tháng (ngày 28-30)"""
        today = fields.Date.today()
        
        # Chỉ nhắc từ ngày 28 đến cuối tháng
        if today.day < 28:
            return
        
        # Lấy bảng công chưa khóa của tháng hiện tại
        work_entries = self.search([
            ('date', '=', today.replace(day=1)),
            ('state', '!=', 'locked'),
        ])
        
        if work_entries:
            # Gửi thông báo cho HR Manager
            hr_users = self.env.ref('hr.group_hr_manager').users
            for user in hr_users:
                self.env['mail.activity'].create({
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    'summary': f'Nhắc nhở: Chốt công tháng {today.strftime("%m/%Y")}',
                    'note': f'Còn {len(work_entries)} bảng công chưa được chốt. Vui lòng kiểm tra và chốt công trước khi tính lương.',
                    'res_model_id': self.env['ir.model']._get_id('hr.work.entry.btl'),
                    'res_id': work_entries[0].id,
                    'user_id': user.id,
                })
