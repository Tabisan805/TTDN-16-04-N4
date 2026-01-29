# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrOvertime(models.Model):
    _name = 'hr.overtime'
    _description = 'Tăng ca'
    _order = 'date desc'
    _rec_name = 'employee_id'
    
    employee_id = fields.Many2one('hr.employee', string='Nhân viên', required=True, ondelete='cascade')
    department_id = fields.Many2one('hr.department', string='Phòng ban', related='employee_id.department_id', store=True)
    
    # Thời gian tăng ca
    date = fields.Date(string='Ngày tăng ca', required=True, default=fields.Date.today)
    time_from = fields.Float(string='Từ giờ', required=True, help='Ví dụ: 18.0 = 6:00 PM')
    time_to = fields.Float(string='Đến giờ', required=True)
    hours = fields.Float(string='Số giờ', compute='_compute_hours', store=True)
    
    # Loại tăng ca
    overtime_type = fields.Selection([
        ('normal', 'Ngày thường'),
        ('weekend', 'Cuối tuần'),
        ('holiday', 'Ngày lễ'),
    ], string='Loại tăng ca', required=True, default='normal')
    
    # Hệ số
    rate = fields.Float(string='Hệ số', compute='_compute_rate', store=True)
    overtime_pay = fields.Float(string='Tiền tăng ca', compute='_compute_overtime_pay', store=True)
    
    # Trạng thái
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('submitted', 'Chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('refused', 'Từ chối'),
    ], string='Trạng thái', default='draft', required=True)
    
    # Ghi chú
    reason = fields.Text(string='Lý do tăng ca')
    note = fields.Text(string='Ghi chú')
    
    # Duyệt
    approved_by = fields.Many2one('res.users', string='Người duyệt')
    approved_date = fields.Datetime(string='Ngày duyệt')
    
    @api.depends('time_from', 'time_to')
    def _compute_hours(self):
        for record in self:
            if record.time_from and record.time_to:
                record.hours = record.time_to - record.time_from
            else:
                record.hours = 0.0
    
    @api.depends('overtime_type', 'employee_id')
    def _compute_rate(self):
        for record in self:
            if record.employee_id:
                if record.overtime_type == 'normal':
                    record.rate = record.employee_id.overtime_rate_normal
                elif record.overtime_type == 'weekend':
                    record.rate = record.employee_id.overtime_rate_weekend
                else:  # holiday
                    record.rate = record.employee_id.overtime_rate_holiday
            else:
                record.rate = 1.5
    
    @api.depends('hours', 'rate', 'employee_id')
    def _compute_overtime_pay(self):
        for record in self:
            if record.employee_id and record.hours:
                # Tính lương theo giờ
                if record.employee_id.wage_type == 'monthly':
                    hourly_rate = record.employee_id.basic_wage / (record.employee_id.standard_working_days * record.employee_id.standard_working_hours)
                elif record.employee_id.wage_type == 'daily':
                    hourly_rate = record.employee_id.basic_wage / record.employee_id.standard_working_hours
                else:  # hourly
                    hourly_rate = record.employee_id.basic_wage
                
                record.overtime_pay = hourly_rate * record.hours * record.rate
            else:
                record.overtime_pay = 0.0
    
    @api.constrains('time_from', 'time_to')
    def _check_times(self):
        for record in self:
            if record.time_to <= record.time_from:
                raise ValidationError(_('Giờ kết thúc phải sau giờ bắt đầu!'))
    
    def action_submit(self):
        self.write({'state': 'submitted'})
    
    def action_approve(self):
        self.write({
            'state': 'approved',
            'approved_by': self.env.user.id,
            'approved_date': fields.Datetime.now(),
        })
    
    def action_refuse(self):
        self.write({'state': 'refused'})
    
    def action_draft(self):
        self.write({'state': 'draft'})
