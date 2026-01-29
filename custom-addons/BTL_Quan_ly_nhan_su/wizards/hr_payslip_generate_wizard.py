# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta


class HrPayslipGenerateWizard(models.TransientModel):
    _name = 'hr.payslip.generate.wizard'
    _description = 'Wizard tạo bảng lương hàng loạt'
    
    date = fields.Date(string='Tháng', required=True, default=fields.Date.today)
    department_ids = fields.Many2many('hr.department', string='Phòng ban')
    employee_ids = fields.Many2many('hr.employee', string='Nhân viên')
    
    generate_all = fields.Boolean(string='Tạo cho tất cả nhân viên', default=True)
    
    @api.onchange('generate_all')
    def _onchange_generate_all(self):
        if self.generate_all:
            self.department_ids = False
            self.employee_ids = False
    
    def action_generate(self):
        """Tạo bảng lương hàng loạt"""
        employees = self.env['hr.employee']
        
        if self.generate_all:
            employees = self.env['hr.employee'].search([('status', '=', 'working')])
        elif self.department_ids:
            employees = self.env['hr.employee'].search([
                ('department_id', 'in', self.department_ids.ids),
                ('status', '=', 'working'),
            ])
        elif self.employee_ids:
            employees = self.employee_ids.filtered(lambda e: e.status == 'working')
        
        if not employees:
            raise UserError(_('Không tìm thấy nhân viên nào phù hợp!'))
        
        # Tạo bảng lương
        payslips = self.env['hr.payslip.btl']
        for employee in employees:
            # Kiểm tra đã tồn tại chưa
            existing = self.env['hr.payslip.btl'].search([
                ('employee_id', '=', employee.id),
                ('date', '=', self.date),
            ])
            
            if existing:
                continue
            
            # Tạo mới
            payslip = payslips.create({
                'employee_id': employee.id,
                'date': self.date,
            })
            
            # Tính toán
            payslip.action_compute_sheet()
            payslips |= payslip
        
        return {
            'name': _('Bảng lương'),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.payslip.btl',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', payslips.ids)],
            'context': {'create': False},
        }
