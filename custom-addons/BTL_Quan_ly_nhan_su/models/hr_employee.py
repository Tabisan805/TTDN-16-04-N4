# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    # Thông tin cơ bản
    employee_code = fields.Char(string='Mã nhân viên', copy=False, default='/', readonly=True)
    join_date = fields.Date(string='Ngày vào làm', default=fields.Date.today, tracking=True)
    status = fields.Selection([
        ('working', 'Đang làm việc'),
        ('resigned', 'Nghỉ việc'),
        ('suspended', 'Tạm nghỉ'),
    ], string='Trạng thái', default='working', required=True, tracking=True)
    resign_date = fields.Date(string='Ngày nghỉ việc', tracking=True)
    
    # Quản lý
    manager_id = fields.Many2one('hr.employee', string='Quản lý trực tiếp', tracking=True)
    
    # Quản lý phép năm
    annual_leave_quota = fields.Float(string='Số phép năm được hưởng', default=12.0, tracking=True,
                                      help='Số ngày phép năm mà nhân viên được hưởng (mặc định 12 ngày/năm)')
    annual_leave_used = fields.Float(string='Số phép đã sử dụng', compute='_compute_annual_leave', store=True,
                                     help='Số ngày phép năm đã sử dụng trong năm hiện tại')
    annual_leave_remaining = fields.Float(string='Số phép còn lại', compute='_compute_annual_leave', store=True,
                                          help='Số ngày phép năm còn lại = Được hưởng - Đã sử dụng')
    
    # Thông tin lương
    wage_type = fields.Selection([
        ('monthly', 'Theo tháng'),
        ('daily', 'Theo ngày công'),
        ('hourly', 'Theo giờ'),
    ], string='Hình thức tính lương', default='monthly', required=True)
    basic_wage = fields.Float(string='Lương cơ bản', default=0)
    
    # Chính sách thưởng
    enable_kpi_bonus = fields.Boolean(string='Thưởng KPI', default=True)
    kpi_target = fields.Float(string='KPI mục tiêu (%)', default=100.0)
    kpi_bonus_rate = fields.Float(string='Tỷ lệ thưởng KPI (%)', help='Tỷ lệ % lương cơ bản khi đạt 100% KPI')
    
    has_commission = fields.Boolean(string='Áp dụng hoa hồng', default=False,
                                    help='Bật hoa hồng doanh số cho nhân viên sale')
    commission_rate = fields.Float(string='Tỷ lệ hoa hồng (%)', default=4.0,
                                   help='Tỷ lệ % hoa hồng trên doanh thu đơn hàng')
    
    # Chế độ tăng ca
    overtime_rate_normal = fields.Float(string='Hệ số tăng ca ngày thường', default=1.5)
    overtime_rate_weekend = fields.Float(string='Hệ số tăng ca cuối tuần', default=2.0)
    overtime_rate_holiday = fields.Float(string='Hệ số tăng ca ngày lễ', default=3.0)
    
    # Chấm công
    standard_working_hours = fields.Float(string='Giờ làm chuẩn/ngày', default=8.0)
    standard_working_days = fields.Float(string='Số ngày công chuẩn/tháng', default=26.0)
    
    # Quan hệ
    attendance_ids = fields.One2many('hr.attendance.btl', 'employee_id', string='Chấm công')
    leave_ids = fields.One2many('hr.leave.btl', 'employee_id', string='Nghỉ phép')
    overtime_ids = fields.One2many('hr.overtime', 'employee_id', string='Tăng ca')
    reward_punishment_ids = fields.One2many('hr.reward.punishment', 'employee_id', string='Thưởng phạt')
    payslip_ids = fields.One2many('hr.payslip.btl', 'employee_id', string='Bảng lương')
    performance_ids = fields.One2many('hr.performance', 'employee_id', string='Hiệu suất')
    
    # Khách hàng phụ trách (liên kết qua user_id)
    partner_ids = fields.One2many('res.partner', 'user_id', 
                                   string='Khách hàng phụ trách',
                                   domain=[('customer_rank', '>', 0)],
                                   related_sudo=False,
                                   help='Danh sách khách hàng mà nhân viên này đang phụ trách')
    partner_count = fields.Integer(string='Số khách hàng', compute='_compute_partner_count', store=True)
    
    # Cơ hội (Leads) phụ trách
    lead_ids = fields.One2many('crm.lead', 'user_id',
                               string='Cơ hội phụ trách',
                               related_sudo=False,
                               help='Danh sách cơ hội/leads mà nhân viên này đang phụ trách')
    lead_count = fields.Integer(string='Số cơ hội', compute='_compute_lead_count', store=True)
    
    # Tính toán
    total_work_days = fields.Float(string='Tổng ngày công', compute='_compute_work_statistics', store=True)
    total_overtime = fields.Float(string='Tổng giờ tăng ca', compute='_compute_work_statistics', store=True, compute_sudo=True)
    current_month_salary = fields.Float(string='Lương tháng hiện tại', compute='_compute_current_salary')
    
    # Doanh thu và hoa hồng
    sales_today = fields.Monetary(string='Doanh thu hôm nay', compute='_compute_sales_statistics', currency_field='currency_id')
    sales_this_month = fields.Monetary(string='Doanh thu tháng này', compute='_compute_sales_statistics', store=True, currency_field='currency_id')
    commission_today = fields.Monetary(string='Hoa hồng hôm nay', compute='_compute_sales_statistics', currency_field='currency_id')
    commission_this_month = fields.Monetary(string='Hoa hồng tháng này', compute='_compute_sales_statistics', store=True, currency_field='currency_id')
    commission_rate = fields.Float(string='Tỷ lệ hoa hồng (%)', default=4.0, help='Tỷ lệ % hoa hồng trên doanh thu')
    total_orders_today = fields.Integer(string='Đơn hàng hôm nay', compute='_compute_sales_statistics')
    total_orders_this_month = fields.Integer(string='Đơn hàng tháng này', compute='_compute_sales_statistics', store=True)
    currency_id = fields.Many2one('res.currency', string='Tiền tệ', default=lambda self: self.env.company.currency_id)
    
    @api.depends('leave_ids.state', 'leave_ids.number_of_days', 'leave_ids.leave_type', 'annual_leave_quota')
    def _compute_annual_leave(self):
        """Tính số phép năm đã sử dụng và còn lại"""
        for employee in self:
            # Lấy năm hiện tại
            current_year = fields.Date.today().year
            year_start = date(current_year, 1, 1)
            year_end = date(current_year, 12, 31)
            
            # Lấy tất cả nghỉ phép năm đã được duyệt trong năm này
            annual_leaves = employee.leave_ids.filtered(
                lambda l: l.leave_type == 'annual' and 
                         l.state == 'approved' and
                         l.date_from >= year_start and
                         l.date_from <= year_end
            )
            
            # Tính tổng số ngày phép đã dùng
            employee.annual_leave_used = sum(annual_leaves.mapped('number_of_days'))
            employee.annual_leave_remaining = employee.annual_leave_quota - employee.annual_leave_used
    
    @api.depends('attendance_ids', 'overtime_ids')
    def _compute_work_statistics(self):
        for employee in self:
            # Tính tổng ngày công tháng hiện tại
            current_month = fields.Date.today().replace(day=1)
            attendances = employee.attendance_ids.filtered(
                lambda a: a.date >= current_month and a.state == 'validated'
            )
            employee.total_work_days = sum(attendances.mapped('work_days'))
            
            # Tính tổng giờ tăng ca
            overtimes = employee.overtime_ids.filtered(
                lambda o: o.date >= current_month and o.state == 'approved'
            )
            employee.total_overtime = sum(overtimes.mapped('hours'))
    
    @api.depends('basic_wage', 'total_work_days', 'wage_type')
    def _compute_current_salary(self):
        for employee in self:
            if employee.wage_type == 'monthly':
                base = employee.basic_wage
            elif employee.wage_type == 'daily':
                base = employee.basic_wage * employee.total_work_days
            else:  # hourly
                base = employee.basic_wage * employee.total_work_days * employee.standard_working_hours
            
            employee.current_month_salary = base
    
    @api.depends('user_id')
    def _compute_partner_count(self):
        for employee in self:
            if employee.user_id:
                partners = self.env['res.partner'].search([
                    ('user_id', '=', employee.user_id.id),
                    ('customer_rank', '>', 0)
                ])
                employee.partner_count = len(partners)
            else:
                employee.partner_count = 0
    
    @api.depends('user_id')
    def _compute_lead_count(self):
        for employee in self:
            if employee.user_id:
                leads = self.env['crm.lead'].search([
                    ('user_id', '=', employee.user_id.id)
                ])
                employee.lead_count = len(leads)
            else:
                employee.lead_count = 0
    
    def action_view_customers(self):
        """Xem danh sách khách hàng phụ trách"""
        self.ensure_one()
        return {
            'name': f'Khách hàng của {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'view_mode': 'tree,form',
            'domain': [('user_id', '=', self.user_id.id), ('customer_rank', '>', 0)],
            'context': {'default_user_id': self.user_id.id},
        }
    
    def action_view_leads(self):
        """Xem danh sách cơ hội/leads phụ trách"""
        self.ensure_one()
        return {
            'name': f'Cơ hội của {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'crm.lead',
            'view_mode': 'tree,form',
            'domain': [('user_id', '=', self.user_id.id)],
            'context': {'default_user_id': self.user_id.id},
        }
    
    @api.depends('user_id')
    def _compute_sales_statistics(self):
        """Tính doanh thu và hoa hồng từ đơn hàng"""
        for employee in self:
            if not employee.user_id:
                employee.sales_today = 0
                employee.sales_this_month = 0
                employee.commission_today = 0
                employee.commission_this_month = 0
                employee.total_orders_today = 0
                employee.total_orders_this_month = 0
                continue
            
            today = fields.Date.today()
            month_start = today.replace(day=1)
            
            # Lấy đơn hàng đã xác nhận (state = sale hoặc done)
            SaleOrder = self.env['sale.order']
            
            # Đơn hàng hôm nay
            orders_today = SaleOrder.search([
                ('user_id', '=', employee.user_id.id),
                ('date_order', '>=', datetime.combine(today, time.min)),
                ('date_order', '<=', datetime.combine(today, time.max)),
                ('state', 'in', ['sale', 'done'])
            ])
            
            # Đơn hàng tháng này
            orders_this_month = SaleOrder.search([
                ('user_id', '=', employee.user_id.id),
                ('date_order', '>=', datetime.combine(month_start, time.min)),
                ('date_order', '<=', fields.Datetime.now()),
                ('state', 'in', ['sale', 'done'])
            ])
            
            # Tính doanh thu
            employee.sales_today = sum(orders_today.mapped('amount_total'))
            employee.sales_this_month = sum(orders_this_month.mapped('amount_total'))
            
            # Tính hoa hồng (4%)
            employee.commission_today = employee.sales_today * (employee.commission_rate / 100)
            employee.commission_this_month = employee.sales_this_month * (employee.commission_rate / 100)
            
            # Số đơn hàng
            employee.total_orders_today = len(orders_today)
            employee.total_orders_this_month = len(orders_this_month)
    
    def action_view_sales_orders(self):
        """Xem đơn hàng của nhân viên"""
        self.ensure_one()
        return {
            'name': f'Đơn hàng của {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'domain': [('user_id', '=', self.user_id.id)],
            'context': {'default_user_id': self.user_id.id},
        }
    
    @api.model_create_multi
    def create(self, vals_list):
        """Override create để tạo mã nhân viên tự động"""
        for vals in vals_list:
            if not vals.get('employee_code') or vals.get('employee_code') == '/':
                vals['employee_code'] = self.env['ir.sequence'].next_by_code('hr.employee.code') or '/'
        return super(HrEmployee, self).create(vals_list)
    
    _sql_constraints = [
        ('employee_code_unique', 'UNIQUE(employee_code)', 'Mã nhân viên đã tồn tại!'),
    ]
