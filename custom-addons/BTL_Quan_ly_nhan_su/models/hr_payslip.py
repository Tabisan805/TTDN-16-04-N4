# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class HrPayslip(models.Model):
    _name = 'hr.payslip.btl'
    _description = 'Bảng lương'
    _order = 'date desc'
    _rec_name = 'employee_id'
    
    employee_id = fields.Many2one('hr.employee', string='Nhân viên', required=True, ondelete='cascade')
    department_id = fields.Many2one('hr.department', string='Phòng ban', related='employee_id.department_id', store=True)
    
    # Kỳ lương
    date = fields.Date(string='Tháng', required=True, default=fields.Date.today)
    date_from = fields.Date(string='Từ ngày', compute='_compute_period', store=True)
    date_to = fields.Date(string='Đến ngày', compute='_compute_period', store=True)
    name = fields.Char(string='Tên', compute='_compute_name', store=True)
    
    # Lương cơ bản
    wage_type = fields.Selection(related='employee_id.wage_type', string='Hình thức tính lương')
    basic_wage = fields.Float(string='Lương cơ bản', related='employee_id.basic_wage')
    
    # Ngày công
    work_days = fields.Float(string='Ngày công thực tế')
    standard_work_days = fields.Float(string='Ngày công chuẩn', related='employee_id.standard_working_days')
    
    # Tính lương cơ bản
    base_salary = fields.Float(string='Lương theo ngày công', compute='_compute_salary', store=True)
    
    # Tăng ca
    overtime_hours = fields.Float(string='Giờ tăng ca')
    overtime_amount = fields.Float(string='Tiền tăng ca', compute='_compute_overtime_amount', store=True)
    
    # Thưởng
    kpi_achievement = fields.Float(string='KPI đạt được (%)')
    kpi_bonus = fields.Float(string='Thưởng KPI', compute='_compute_kpi_bonus', store=True)
    
    # Hoa hồng doanh số (commission)
    commission_amount = fields.Float(string='Hoa hồng doanh số', compute='_compute_commission', store=True,
                                     help='Hoa hồng tính từ dựa trên doanh thu đơn hàng')
    commission_rate = fields.Float(string='Tỷ lệ hoa hồng (%)', related='employee_id.commission_rate')
    
    attendance_bonus = fields.Float(string='Thưởng chuyên cần')
    other_bonus = fields.Float(string='Các khoản thưởng khác')
    total_bonus = fields.Float(string='Tổng thưởng', compute='_compute_total_bonus_punishment', store=True)
    
    # Phạt
    late_punishment = fields.Float(string='Phạt đi trễ')
    other_punishment = fields.Float(string='Các khoản phạt khác')
    total_punishment = fields.Float(string='Tổng phạt', compute='_compute_total_bonus_punishment', store=True)
    
    # Tổng thu nhập
    gross_salary = fields.Float(string='Tổng thu nhập', compute='_compute_gross_salary', store=True)
    
    # Khấu trừ
    insurance_amount = fields.Float(string='Bảo hiểm')
    tax_amount = fields.Float(string='Thuế TNCN')
    other_deduction = fields.Float(string='Khấu trừ khác')
    total_deduction = fields.Float(string='Tổng khấu trừ', compute='_compute_total_deduction', store=True)
    
    # Thực lãnh
    net_salary = fields.Float(string='Thực lãnh', compute='_compute_net_salary', store=True)
    
    # Chi tiết
    reward_punishment_ids = fields.One2many('hr.reward.punishment', 'payslip_id', string='Chi tiết thưởng phạt')
    work_entry_id = fields.Many2one('hr.work.entry.btl', string='Bảng công')
    
    # Trạng thái
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('confirmed', 'Đã xác nhận'),
        ('paid', 'Đã thanh toán'),
        ('cancelled', 'Đã hủy'),
    ], string='Trạng thái', default='draft', required=True)
    
    # Thanh toán
    payment_date = fields.Date(string='Ngày thanh toán')
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
    
    @api.depends('employee_id', 'date')
    def _compute_name(self):
        for record in self:
            if record.employee_id and record.date:
                record.name = f"Lương {record.employee_id.name} - {record.date.strftime('%m/%Y')}"
            else:
                record.name = "Bảng lương"
    
    @api.depends('basic_wage', 'work_days', 'standard_work_days', 'wage_type')
    def _compute_salary(self):
        for record in self:
            if record.wage_type == 'monthly':
                # Lương tháng tính theo tỷ lệ ngày công
                record.base_salary = record.basic_wage * record.work_days / record.standard_work_days
            elif record.wage_type == 'daily':
                record.base_salary = record.basic_wage * record.work_days
            else:  # hourly
                record.base_salary = record.basic_wage * record.work_days * record.employee_id.standard_working_hours
    
    @api.depends('overtime_hours', 'employee_id')
    def _compute_overtime_amount(self):
        for record in self:
            if record.employee_id and record.overtime_hours:
                # Lấy từ overtime records
                overtimes = self.env['hr.overtime'].search([
                    ('employee_id', '=', record.employee_id.id),
                    ('date', '>=', record.date_from),
                    ('date', '<=', record.date_to),
                    ('state', '=', 'approved'),
                ])
                record.overtime_amount = sum(overtimes.mapped('overtime_pay'))
            else:
                record.overtime_amount = 0.0
    
    @api.depends('kpi_achievement', 'basic_wage', 'employee_id')
    def _compute_kpi_bonus(self):
        for record in self:
            if record.employee_id.enable_kpi_bonus and record.kpi_achievement >= record.employee_id.kpi_target:
                # Thưởng KPI dựa trên tỷ lệ đạt được
                rate = record.kpi_achievement / 100
                record.kpi_bonus = record.basic_wage * record.employee_id.kpi_bonus_rate / 100 * rate
            else:
                record.kpi_bonus = 0.0
    
    @api.depends('employee_id', 'date_from', 'date_to', 'commission_rate')
    def _compute_commission(self):
        """Tính hoa hồng từ doanh thu đơn hàng"""
        for record in self:
            if not record.employee_id or not record.employee_id.user_id or not record.date_from or not record.date_to:
                record.commission_amount = 0.0
                continue
            
            # Chỉ tính hoa hồng nếu nhân viên có bật hoa hồng
            if not record.employee_id.has_commission:
                record.commission_amount = 0.0
                continue
            
            # Lấy đơn hàng đã xác nhận trong kỳ
            SaleOrder = self.env['sale.order']
            orders = SaleOrder.search([
                ('user_id', '=', record.employee_id.user_id.id),
                ('date_order', '>=', fields.Datetime.combine(record.date_from, fields.Datetime.min.time())),
                ('date_order', '<=', fields.Datetime.combine(record.date_to, fields.Datetime.max.time())),
                ('state', 'in', ['sale', 'done'])
            ])
            
            # Tính tổng doanh thu
            total_sales = sum(orders.mapped('amount_total'))
            
            # Tính hoa hồng theo tỷ lệ %
            record.commission_amount = total_sales * (record.commission_rate / 100)
    
    @api.depends('kpi_bonus', 'commission_amount', 'attendance_bonus', 'other_bonus')
    def _compute_total_bonus_punishment(self):
        for record in self:
            record.total_bonus = record.kpi_bonus + record.commission_amount + record.attendance_bonus + record.other_bonus
            record.total_punishment = record.late_punishment + record.other_punishment
    
    @api.depends('base_salary', 'overtime_amount', 'total_bonus', 'total_punishment')
    def _compute_gross_salary(self):
        for record in self:
            record.gross_salary = record.base_salary + record.overtime_amount + record.total_bonus - record.total_punishment
    
    @api.depends('insurance_amount', 'tax_amount', 'other_deduction')
    def _compute_total_deduction(self):
        for record in self:
            record.total_deduction = record.insurance_amount + record.tax_amount + record.other_deduction
    
    @api.depends('gross_salary', 'total_deduction')
    def _compute_net_salary(self):
        for record in self:
            record.net_salary = record.gross_salary - record.total_deduction
    
    def action_compute_sheet(self):
        """Tính toán bảng lương tự động"""
        for record in self:
            # Lấy bảng công
            work_entry = self.env['hr.work.entry.btl'].search([
                ('employee_id', '=', record.employee_id.id),
                ('date', '=', record.date),
            ], limit=1)
            
            if work_entry:
                record.work_entry_id = work_entry.id
                record.work_days = work_entry.total_work_days
                record.overtime_hours = work_entry.total_overtime
            else:
                # Nếu không có bảng công, tính từ chấm công và nghỉ phép
                attendances = self.env['hr.attendance.btl'].search([
                    ('employee_id', '=', record.employee_id.id),
                    ('date', '>=', record.date_from),
                    ('date', '<=', record.date_to),
                    ('state', '=', 'validated'),
                ])
                work_days_from_attendance = sum(attendances.mapped('work_days'))
                
                # Lấy nghỉ phép có lương (annual leave, sick leave có phép)
                paid_leaves = self.env['hr.leave.btl'].search([
                    ('employee_id', '=', record.employee_id.id),
                    ('date_from', '>=', record.date_from),
                    ('date_to', '<=', record.date_to),
                    ('state', '=', 'approved'),
                    ('is_paid', '=', True),
                ])
                leave_days_paid = sum(paid_leaves.mapped('number_of_days'))
                
                # Tổng công = Công chấm công + Nghỉ phép có lương
                record.work_days = work_days_from_attendance + leave_days_paid
                
                # Tăng ca
                overtimes = self.env['hr.overtime'].search([
                    ('employee_id', '=', record.employee_id.id),
                    ('date', '>=', record.date_from),
                    ('date', '<=', record.date_to),
                    ('state', '=', 'approved'),
                ])
                record.overtime_hours = sum(overtimes.mapped('hours'))
            
            # Lấy thưởng phạt
            rewards_punishments = self.env['hr.reward.punishment'].search([
                ('employee_id', '=', record.employee_id.id),
                ('date', '>=', record.date_from),
                ('date', '<=', record.date_to),
                ('state', '=', 'confirmed'),
                ('payslip_id', '=', False),
            ])
            
            # Gán vào bảng lương
            rewards_punishments.write({'payslip_id': record.id, 'state': 'applied'})
            
            # Tính thưởng phạt
            rewards = rewards_punishments.filtered(lambda r: r.type == 'reward')
            punishments = rewards_punishments.filtered(lambda r: r.type == 'punishment')
            
            record.other_bonus = sum(rewards.mapped('amount'))
            record.other_punishment = sum(punishments.mapped('amount'))
            
            # Lấy hiệu suất
            performance = self.env['hr.performance'].search([
                ('employee_id', '=', record.employee_id.id),
                ('date', '>=', record.date_from),
                ('date', '<=', record.date_to),
            ], limit=1, order='date desc')
            
            if performance:
                record.kpi_achievement = performance.kpi_achievement
    
    def action_confirm(self):
        self.write({'state': 'confirmed'})
    
    def action_paid(self):
        self.write({
            'state': 'paid',
            'payment_date': fields.Date.today(),
        })
    
    def action_cancel(self):
        # Hủy liên kết thưởng phạt
        self.reward_punishment_ids.write({'payslip_id': False, 'state': 'confirmed'})
        self.write({'state': 'cancelled'})
    
    def action_draft(self):
        if self.state == 'paid':
            raise ValidationError(_('Không thể chuyển về nháp khi đã thanh toán!'))
        # Hủy liên kết thưởng phạt
        self.reward_punishment_ids.write({'payslip_id': False, 'state': 'confirmed'})
        self.write({'state': 'draft'})
    
    _sql_constraints = [
        ('employee_date_unique', 'UNIQUE(employee_id, date)', 
         'Đã tồn tại bảng lương cho nhân viên này trong tháng này!'),
    ]
