# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrAttendanceRule(models.Model):
    _name = 'hr.attendance.rule'
    _description = 'Quy định chấm công'
    
    name = fields.Char(string='Tên quy định', required=True)
    active = fields.Boolean(string='Hoạt động', default=True)
    
    # Giờ làm việc chuẩn
    work_time_start = fields.Float(string='Giờ vào chuẩn', default=8.0, help='Ví dụ: 8.0 = 8:00 AM')
    work_time_end = fields.Float(string='Giờ ra chuẩn', default=17.0, help='Ví dụ: 17.0 = 5:00 PM')
    lunch_break_start = fields.Float(string='Bắt đầu giờ nghỉ trưa', default=12.0)
    lunch_break_end = fields.Float(string='Kết thúc giờ nghỉ trưa', default=13.0)
    
    # Quy định đi trễ, về sớm
    late_tolerance_minutes = fields.Integer(string='Dung sai đi trễ (phút)', default=15, 
                                           help='Số phút được phép đi trễ mà không bị tính thiếu công')
    early_leave_tolerance_minutes = fields.Integer(string='Dung sai về sớm (phút)', default=15)
    
    # Tính công
    late_deduction_per_minute = fields.Float(string='Trừ công theo phút trễ', default=0.01,
                                            help='Số ngày công bị trừ cho mỗi phút đi trễ')
    early_deduction_per_minute = fields.Float(string='Trừ công theo phút về sớm', default=0.01)
    absent_deduction = fields.Float(string='Trừ công khi vắng mặt', default=1.0)
    
    # Phạt tiền
    late_fine_per_time = fields.Float(string='Phạt mỗi lần đi trễ (VNĐ)', default=0.0)
    early_fine_per_time = fields.Float(string='Phạt mỗi lần về sớm (VNĐ)', default=0.0)
    absent_fine_per_day = fields.Float(string='Phạt vắng mặt không phép (VNĐ)', default=0.0)
    
    # Thưởng chuyên cần
    perfect_attendance_bonus = fields.Float(string='Thưởng chuyên cần (VNĐ)', default=0.0,
                                           help='Thưởng khi đi làm đầy đủ, không trễ, không sớm')
    perfect_attendance_days_required = fields.Integer(string='Số ngày công cần đạt', default=26)
    
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
