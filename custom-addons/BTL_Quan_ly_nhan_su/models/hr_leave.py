# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date


class HrLeave(models.Model):
    _name = 'hr.leave.btl'
    _description = 'Nghỉ phép'
    _order = 'date_from desc'
    _rec_name = 'employee_id'
    
    employee_id = fields.Many2one('hr.employee', string='Nhân viên', required=True, ondelete='cascade')
    department_id = fields.Many2one('hr.department', string='Phòng ban', related='employee_id.department_id', store=True)
    
    # Thời gian nghỉ
    date_from = fields.Date(string='Từ ngày', required=True)
    date_to = fields.Date(string='Đến ngày', required=True)
    number_of_days = fields.Float(string='Số ngày nghỉ', compute='_compute_number_of_days', store=True)
    
    # Loại nghỉ
    leave_type = fields.Selection([
        ('annual', 'Nghỉ phép năm'),
        ('sick', 'Nghỉ ốm'),
        ('unpaid', 'Nghỉ không lương'),
        ('maternity', 'Nghỉ thai sản'),
        ('other', 'Khác'),
    ], string='Loại nghỉ phép', required=True, default='annual')
    
    is_approved = fields.Boolean(string='Có phép', default=True, 
                                 help='Nghỉ có phép = được duyệt và được tính công')
    is_paid = fields.Boolean(string='Hưởng lương', default=True)
    
    # Trạng thái
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('submitted', 'Chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('refused', 'Từ chối'),
        ('cancelled', 'Đã hủy'),
    ], string='Trạng thái', default='draft', required=True)
    
    # Ghi chú
    reason = fields.Text(string='Lý do nghỉ')
    note = fields.Text(string='Ghi chú')
    
    # Duyệt
    approved_by = fields.Many2one('res.users', string='Người duyệt')
    approved_date = fields.Datetime(string='Ngày duyệt')
    refused_reason = fields.Text(string='Lý do từ chối')
    
    @api.depends('date_from', 'date_to')
    def _compute_number_of_days(self):
        for record in self:
            if record.date_from and record.date_to:
                delta = record.date_to - record.date_from
                record.number_of_days = delta.days + 1
            else:
                record.number_of_days = 0
    
    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for record in self:
            if record.date_to < record.date_from:
                raise ValidationError(_('Ngày kết thúc phải sau ngày bắt đầu!'))
    
    @api.constrains('employee_id', 'leave_type', 'number_of_days', 'state')
    def _check_annual_leave_quota(self):
        """Kiểm tra số phép năm còn lại khi duyệt nghỉ phép năm"""
        for record in self:
            if record.leave_type == 'annual' and record.state == 'approved':
                # Lấy số phép còn lại của nhân viên (không tính leave hiện tại)
                current_year = fields.Date.today().year
                other_leaves = self.search([
                    ('employee_id', '=', record.employee_id.id),
                    ('leave_type', '=', 'annual'),
                    ('state', '=', 'approved'),
                    ('id', '!=', record.id),
                    ('date_from', '>=', date(current_year, 1, 1)),
                ])
                used = sum(other_leaves.mapped('number_of_days'))
                remaining = record.employee_id.annual_leave_quota - used
                
                if record.number_of_days > remaining:
                    raise ValidationError(_(
                        'Không đủ phép năm! Nhân viên %s còn %.1f ngày phép, '
                        'nhưng đang đăng ký %.1f ngày.'
                    ) % (record.employee_id.name, remaining, record.number_of_days))
    
    def action_submit(self):
        self.write({'state': 'submitted'})
    
    def action_approve(self):
        """Duyệt nghỉ phép - Kiểm tra phép năm trước khi duyệt"""
        for record in self:
            # Kiểm tra phép năm
            if record.leave_type == 'annual':
                if record.number_of_days > record.employee_id.annual_leave_remaining:
                    raise ValidationError(_(
                        'Không thể duyệt! Nhân viên %s chỉ còn %.1f ngày phép năm, '
                        'nhưng đang yêu cầu %.1f ngày.'
                    ) % (record.employee_id.name, record.employee_id.annual_leave_remaining, 
                          record.number_of_days))
        
        self.write({
            'state': 'approved',
            'approved_by': self.env.user.id,
            'approved_date': fields.Datetime.now(),
        })
    
    def action_refuse(self):
        self.write({'state': 'refused'})
    
    def action_cancel(self):
        self.write({'state': 'cancelled'})
    
    def action_draft(self):
        self.write({'state': 'draft'})
