# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HrRewardPunishment(models.Model):
    _name = 'hr.reward.punishment'
    _description = 'Thưởng - Phạt'
    _order = 'date desc'
    _rec_name = 'employee_id'
    
    employee_id = fields.Many2one('hr.employee', string='Nhân viên', required=True, ondelete='cascade')
    department_id = fields.Many2one('hr.department', string='Phòng ban', related='employee_id.department_id', store=True)
    
    # Loại thưởng phạt
    type_id = fields.Many2one('hr.reward.punishment.type', string='Loại', required=True)
    type = fields.Selection(related='type_id.type', string='Phân loại', store=True)
    
    # Thời gian
    date = fields.Date(string='Ngày', required=True, default=fields.Date.today)
    period = fields.Char(string='Kỳ áp dụng', help='Ví dụ: 01/2026')
    
    # Số tiền
    amount = fields.Float(string='Số tiền', required=True)
    
    # Trạng thái
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('confirmed', 'Đã xác nhận'),
        ('applied', 'Đã áp dụng vào lương'),
    ], string='Trạng thái', default='draft', required=True)
    
    # Ghi chú
    reason = fields.Text(string='Lý do', required=True)
    note = fields.Text(string='Ghi chú')
    
    # Người tạo và duyệt
    created_by = fields.Many2one('res.users', string='Người tạo', default=lambda self: self.env.user)
    approved_by = fields.Many2one('res.users', string='Người duyệt')
    approved_date = fields.Datetime(string='Ngày duyệt')
    
    # Liên kết với bảng lương
    payslip_id = fields.Many2one('hr.payslip.btl', string='Bảng lương')
    
    @api.onchange('type_id')
    def _onchange_type_id(self):
        if self.type_id:
            if self.type_id.amount_type == 'fixed':
                self.amount = self.type_id.default_amount
            elif self.type_id.amount_type == 'percentage' and self.employee_id:
                self.amount = self.employee_id.basic_wage * self.type_id.default_amount / 100
    
    def action_confirm(self):
        self.write({
            'state': 'confirmed',
            'approved_by': self.env.user.id,
            'approved_date': fields.Datetime.now(),
        })
    
    def action_draft(self):
        if self.state == 'applied':
            raise ValidationError(_('Không thể chuyển về nháp khi đã áp dụng vào lương!'))
        self.write({'state': 'draft'})
