# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrDepartment(models.Model):
    _inherit = 'hr.department'
    
    manager_id = fields.Many2one('hr.employee', string='Trưởng phòng')
    kpi_target = fields.Float(string='KPI mục tiêu phòng ban (%)', default=100.0)
    
    # Thống kê
    total_employees = fields.Integer(string='Số lượng nhân viên', compute='_compute_statistics')
    total_work_days = fields.Float(string='Tổng ngày công', compute='_compute_statistics')
    average_kpi = fields.Float(string='KPI trung bình (%)', compute='_compute_statistics')
    
    @api.depends('member_ids')
    def _compute_statistics(self):
        for dept in self:
            employees = dept.member_ids.filtered(lambda e: e.status == 'working')
            dept.total_employees = len(employees)
            dept.total_work_days = sum(employees.mapped('total_work_days'))
            
            # Tính KPI trung bình
            if employees:
                performances = self.env['hr.performance'].search([
                    ('employee_id', 'in', employees.ids),
                    ('date', '>=', fields.Date.today().replace(day=1))
                ])
                if performances:
                    dept.average_kpi = sum(performances.mapped('kpi_achievement')) / len(performances)
                else:
                    dept.average_kpi = 0.0
            else:
                dept.average_kpi = 0.0
