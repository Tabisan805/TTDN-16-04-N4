# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class HrAttendance(models.Model):
    _name = 'hr.attendance.btl'
    _description = 'Chấm công'
    _order = 'date desc, check_in desc'
    _rec_name = 'employee_id'
    
    employee_id = fields.Many2one('hr.employee', string='Nhân viên', required=True, ondelete='cascade')
    department_id = fields.Many2one('hr.department', string='Phòng ban', related='employee_id.department_id', store=True)
    date = fields.Date(string='Ngày', required=True, default=fields.Date.today)
    
    # Thời gian
    check_in = fields.Datetime(string='Giờ vào', required=True)
    check_out = fields.Datetime(string='Giờ ra')
    worked_hours = fields.Float(string='Giờ làm việc', compute='_compute_worked_hours', store=True)
    
    # Tính toán
    is_late = fields.Boolean(string='Đi trễ', compute='_compute_attendance_status', store=True)
    late_minutes = fields.Integer(string='Số phút trễ', compute='_compute_attendance_status', store=True)
    is_early_leave = fields.Boolean(string='Về sớm', compute='_compute_attendance_status', store=True)
    early_minutes = fields.Integer(string='Số phút về sớm', compute='_compute_attendance_status', store=True)
    
    work_days = fields.Float(string='Ngày công', compute='_compute_work_days', store=True)
    
    # Trạng thái
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('confirmed', 'Đã xác nhận'),
        ('validated', 'Đã duyệt'),
    ], string='Trạng thái', default='draft', required=True)
    
    # Ghi chú
    note = fields.Text(string='Ghi chú')
    
    # Quy định áp dụng
    rule_id = fields.Many2one('hr.attendance.rule', string='Quy định chấm công', 
                             default=lambda self: self.env['hr.attendance.rule'].search([('active', '=', True)], limit=1))
    
    @api.depends('check_in', 'check_out')
    def _compute_worked_hours(self):
        for record in self:
            if record.check_in and record.check_out:
                delta = record.check_out - record.check_in
                hours = delta.total_seconds() / 3600
                
                # Trừ giờ nghỉ trưa
                if record.rule_id:
                    lunch_hours = record.rule_id.lunch_break_end - record.rule_id.lunch_break_start
                    hours = max(0, hours - lunch_hours)
                
                record.worked_hours = hours
            else:
                record.worked_hours = 0.0
    
    @api.depends('check_in', 'check_out', 'rule_id')
    def _compute_attendance_status(self):
        for record in self:
            if not record.rule_id or not record.check_in:
                record.is_late = False
                record.late_minutes = 0
                record.is_early_leave = False
                record.early_minutes = 0
                continue
            
            # Chuyển datetime sang time của ngày
            check_in_time = record.check_in.hour + record.check_in.minute / 60.0
            
            # Kiểm tra đi trễ
            if check_in_time > record.rule_id.work_time_start:
                late_minutes = (check_in_time - record.rule_id.work_time_start) * 60
                if late_minutes > record.rule_id.late_tolerance_minutes:
                    record.is_late = True
                    record.late_minutes = int(late_minutes)
                else:
                    record.is_late = False
                    record.late_minutes = 0
            else:
                record.is_late = False
                record.late_minutes = 0
            
            # Kiểm tra về sớm
            if record.check_out:
                check_out_time = record.check_out.hour + record.check_out.minute / 60.0
                if check_out_time < record.rule_id.work_time_end:
                    early_minutes = (record.rule_id.work_time_end - check_out_time) * 60
                    if early_minutes > record.rule_id.early_leave_tolerance_minutes:
                        record.is_early_leave = True
                        record.early_minutes = int(early_minutes)
                    else:
                        record.is_early_leave = False
                        record.early_minutes = 0
                else:
                    record.is_early_leave = False
                    record.early_minutes = 0
            else:
                record.is_early_leave = False
                record.early_minutes = 0
    
    @api.depends('worked_hours', 'is_late', 'late_minutes', 'is_early_leave', 'early_minutes', 'employee_id.standard_working_hours', 'rule_id')
    def _compute_work_days(self):
        for record in self:
            if not record.check_out:
                record.work_days = 0.0
                continue
            
            # Bắt đầu với 1 ngày công đầy đủ
            work_days = 1.0
            
            # Trừ công do đi trễ
            if record.is_late and record.rule_id:
                work_days -= record.late_minutes * record.rule_id.late_deduction_per_minute
            
            # Trừ công do về sớm
            if record.is_early_leave and record.rule_id:
                work_days -= record.early_minutes * record.rule_id.early_deduction_per_minute
            
            # Đảm bảo không âm
            record.work_days = max(0.0, work_days)
    
    def action_confirm(self):
        self.write({'state': 'confirmed'})
    
    def action_validate(self):
        """Duyệt chấm công và tạo phạt tự động nếu đi trễ/về sớm"""
        self.write({'state': 'validated'})
        
        # Tạo phạt tự động
        for record in self:
            if not record.rule_id:
                continue
            
            # Phạt đi trễ
            if record.is_late and record.rule_id.late_fine_per_time > 0:
                self._create_punishment(
                    type_code='LATE',
                    amount=record.rule_id.late_fine_per_time,
                    reason=f'Đi trễ {record.late_minutes} phút ngày {record.date.strftime("%d/%m/%Y")}'
                )
            
            # Phạt về sớm
            if record.is_early_leave and record.rule_id.early_fine_per_time > 0:
                self._create_punishment(
                    type_code='EARLY_LEAVE',
                    amount=record.rule_id.early_fine_per_time,
                    reason=f'Về sớm {record.early_minutes} phút ngày {record.date.strftime("%d/%m/%Y")}'
                )
    
    def _create_punishment(self, type_code, amount, reason):
        """Tạo phạt tự động"""
        self.ensure_one()
        
        # Tìm loại thưởng phạt
        punishment_type = self.env['hr.reward.punishment.type'].search([
            ('code', '=', type_code),
            ('type', '=', 'punishment'),
        ], limit=1)
        
        if not punishment_type:
            # Tạo loại phạt mới nếu chưa có
            punishment_type = self.env['hr.reward.punishment.type'].create({
                'name': 'Phạt ' + ('đi trễ' if type_code == 'LATE' else 'về sớm'),
                'code': type_code,
                'type': 'punishment',
                'amount_type': 'fixed',
                'default_amount': amount,
            })
        
        # Tạo phạt
        self.env['hr.reward.punishment'].create({
            'employee_id': self.employee_id.id,
            'type_id': punishment_type.id,
            'type': 'punishment',
            'date': self.date,
            'amount': amount,
            'reason': reason,
            'state': 'confirmed',
        })
    
    def action_draft(self):
        self.write({'state': 'draft'})
    
    @api.constrains('check_in', 'check_out')
    def _check_check_out_after_check_in(self):
        for record in self:
            if record.check_out and record.check_out <= record.check_in:
                raise ValidationError(_('Giờ ra phải sau giờ vào!'))
    
    @api.constrains('employee_id', 'date', 'state')
    def _check_duplicate_attendance(self):
        """Không cho chấm công trùng ngày"""
        for record in self:
            if record.state in ['confirmed', 'validated']:
                duplicate = self.search([
                    ('employee_id', '=', record.employee_id.id),
                    ('date', '=', record.date),
                    ('id', '!=', record.id),
                    ('state', 'in', ['confirmed', 'validated']),
                ])
                if duplicate:
                    raise ValidationError(_(
                        'Nhân viên %s đã có chấm công cho ngày %s rồi!'
                    ) % (record.employee_id.name, record.date.strftime('%d/%m/%Y')))
    
    @api.constrains('employee_id', 'date')
    def _check_leave_on_same_day(self):
        """Kiểm tra không cho chấm công nếu đang nghỉ phép"""
        for record in self:
            # Kiểm tra nghỉ phép trong ngày
            leave = self.env['hr.leave.btl'].search([
                ('employee_id', '=', record.employee_id.id),
                ('date_from', '<=', record.date),
                ('date_to', '>=', record.date),
                ('state', '=', 'approved'),
            ], limit=1)
            
            if leave:
                raise ValidationError(_(
                    'Nhân viên %s đang nghỉ phép từ %s đến %s. '
                    'Không thể chấm công trong ngày này!'
                ) % (record.employee_id.name, 
                     leave.date_from.strftime('%d/%m/%Y'),
                     leave.date_to.strftime('%d/%m/%Y')))
