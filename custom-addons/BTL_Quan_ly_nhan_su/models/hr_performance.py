# -*- coding: utf-8 -*-

from odoo import models, fields, api
from dateutil.relativedelta import relativedelta


class HrPerformance(models.Model):
    _name = 'hr.performance'
    _description = 'Hiệu suất làm việc'
    _order = 'date desc'
    _rec_name = 'employee_id'
    
    employee_id = fields.Many2one('hr.employee', string='Nhân viên', required=True, ondelete='cascade')
    department_id = fields.Many2one('hr.department', string='Phòng ban', related='employee_id.department_id', store=True)
    
    # Kỳ đánh giá
    date = fields.Date(string='Tháng', required=True, default=fields.Date.today)
    date_from = fields.Date(string='Từ ngày', compute='_compute_period', store=True)
    date_to = fields.Date(string='Đến ngày', compute='_compute_period', store=True)
    
    # KPI
    kpi_target = fields.Float(string='KPI mục tiêu (%)', related='employee_id.kpi_target')
    kpi_achievement = fields.Float(string='KPI đạt được (%)', compute='_compute_kpi', store=True)
    kpi_status = fields.Selection([
        ('below', 'Dưới mục tiêu'),
        ('meet', 'Đạt mục tiêu'),
        ('exceed', 'Vượt mục tiêu'),
    ], string='Trạng thái KPI', compute='_compute_kpi_status', store=True)
    
    # Doanh số (nếu là sales)
    sales_target = fields.Float(string='Mục tiêu doanh số')
    sales_amount = fields.Float(string='Doanh số thực tế', compute='_compute_sales', store=True)
    sales_achievement = fields.Float(string='Tỷ lệ đạt (%)', compute='_compute_sales_achievement', store=True)
    
    # Hoạt động
    total_activities = fields.Integer(string='Số hoạt động', compute='_compute_activities', store=True)
    total_calls = fields.Integer(string='Số cuộc gọi', compute='_compute_activities', store=True)
    total_meetings = fields.Integer(string='Số cuộc họp', compute='_compute_activities', store=True)
    
    # Khách hàng
    total_customers = fields.Integer(string='Số khách hàng phụ trách', compute='_compute_customers', store=True)
    new_customers = fields.Integer(string='Khách hàng mới', compute='_compute_customers', store=True)
    
    # Cơ hội (Leads/Opportunities)
    total_leads = fields.Integer(string='Số cơ hội', compute='_compute_leads', store=True)
    won_leads = fields.Integer(string='Cơ hội thành công', compute='_compute_leads', store=True)
    win_rate = fields.Float(string='Tỷ lệ chốt (%)', compute='_compute_win_rate', store=True)
    
    # Công việc (Tasks)
    total_tasks = fields.Integer(string='Số công việc', compute='_compute_tasks', store=True)
    completed_tasks = fields.Integer(string='Công việc hoàn thành', compute='_compute_tasks', store=True)
    on_time_tasks = fields.Integer(string='Hoàn thành đúng hạn', compute='_compute_tasks', store=True)
    task_completion_rate = fields.Float(string='Tỷ lệ hoàn thành (%)', compute='_compute_task_rate', store=True)
    on_time_rate = fields.Float(string='Tỷ lệ đúng hạn (%)', compute='_compute_task_rate', store=True)
    
    # Đánh giá
    overall_rating = fields.Selection([
        ('1', 'Kém'),
        ('2', 'Trung bình'),
        ('3', 'Khá'),
        ('4', 'Tốt'),
        ('5', 'Xuất sắc'),
    ], string='Đánh giá chung')
    
    # Ghi chú
    strength = fields.Text(string='Điểm mạnh')
    weakness = fields.Text(string='Điểm yếu')
    note = fields.Text(string='Ghi chú')
    
    # Trạng thái
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('confirmed', 'Đã xác nhận'),
    ], string='Trạng thái', default='draft', required=True)
    
    @api.depends('date')
    def _compute_period(self):
        for record in self:
            if record.date:
                record.date_from = record.date.replace(day=1)
                record.date_to = record.date_from + relativedelta(months=1, days=-1)
            else:
                record.date_from = False
                record.date_to = False
    
    @api.depends('sales_amount', 'total_activities', 'won_leads', 'total_tasks', 'completed_tasks', 'on_time_tasks')
    def _compute_kpi(self):
        """Tính KPI tổng hợp từ nhiều yếu tố: doanh số, công việc, lead"""
        for record in self:
            # Tính KPI theo trọng số:
            # - 60% từ doanh số (cho sale) hoặc công việc (cho nhân viên khác)
            # - 20% từ tỷ lệ hoàn thành công việc đúng hạn
            # - 20% từ tỷ lệ chốt lead (cho sale) hoặc hoạt động (cho nhân viên khác)
            
            kpi_sales = 0.0
            kpi_tasks = 0.0
            kpi_leads = 0.0
            
            # 1. KPI Doanh số/Công việc (60%)
            if record.employee_id.has_commission and record.sales_amount > 0:
                # Nhân viên sale: Tính KPI từ doanh số
                if record.sales_target and record.sales_amount:
                    kpi_sales = (record.sales_amount / record.sales_target) * 60
                else:
                    # Không có target, dùng base 10 triệu = 60%
                    base_target = 10000000
                    kpi_sales = min((record.sales_amount / base_target) * 60, 120)
            else:
                # Nhân viên khác: Tính KPI từ tỷ lệ hoàn thành công việc
                if record.total_tasks > 0:
                    kpi_sales = (record.completed_tasks / record.total_tasks) * 60
            
            # 2. KPI Công việc đúng hạn (20%)
            if record.completed_tasks > 0:
                kpi_tasks = (record.on_time_tasks / record.completed_tasks) * 20
            
            # 3. KPI Lead/Hoạt động (20%)
            if record.employee_id.has_commission:
                # Sale: Tỷ lệ chốt lead
                if record.total_leads > 0:
                    kpi_leads = (record.won_leads / record.total_leads) * 20
            else:
                # Nhân viên khác: Hoạt động tối thiểu
                # Giả sử 20 hoạt động/tháng = 20%
                if record.total_activities >= 20:
                    kpi_leads = 20
                else:
                    kpi_leads = (record.total_activities / 20) * 20
            
            # Tổng KPI
            record.kpi_achievement = kpi_sales + kpi_tasks + kpi_leads
    
    @api.depends('kpi_achievement', 'kpi_target')
    def _compute_kpi_status(self):
        for record in self:
            if record.kpi_achievement < record.kpi_target:
                record.kpi_status = 'below'
            elif record.kpi_achievement == record.kpi_target:
                record.kpi_status = 'meet'
            else:
                record.kpi_status = 'exceed'
    
    @api.depends('date_from', 'date_to', 'employee_id')
    def _compute_sales(self):
        """Tính doanh số/doanh thu từ đơn hàng đã chốt"""
        for record in self:
            if not record.date_from or not record.date_to or not record.employee_id or not record.employee_id.user_id:
                record.sales_amount = 0.0
                continue
            
            # Lấy doanh thu từ các đơn hàng đã xác nhận (state = sale hoặc done)
            if self.env['ir.model'].search([('model', '=', 'sale.order')]):
                orders = self.env['sale.order'].search([
                    ('user_id', '=', record.employee_id.user_id.id),
                    ('date_order', '>=', fields.Datetime.combine(record.date_from, fields.Datetime.min.time())),
                    ('date_order', '<=', fields.Datetime.combine(record.date_to, fields.Datetime.max.time())),
                    ('state', 'in', ['sale', 'done']),
                ])
                record.sales_amount = sum(orders.mapped('amount_total'))
            else:
                record.sales_amount = 0.0
    
    @api.depends('sales_amount', 'sales_target')
    def _compute_sales_achievement(self):
        for record in self:
            if record.sales_target:
                record.sales_achievement = (record.sales_amount / record.sales_target) * 100
            else:
                record.sales_achievement = 0.0
    
    @api.depends('date_from', 'date_to', 'employee_id')
    def _compute_activities(self):
        """Tính số hoạt động từ CRM"""
        for record in self:
            if not record.date_from or not record.date_to or not record.employee_id:
                record.total_activities = 0
                record.total_calls = 0
                record.total_meetings = 0
                continue
            
            if self.env['ir.model'].search([('model', '=', 'mail.activity')]):
                activities = self.env['mail.activity'].search([
                    ('user_id', '=', record.employee_id.user_id.id),
                    ('date_deadline', '>=', record.date_from),
                    ('date_deadline', '<=', record.date_to),
                ])
                record.total_activities = len(activities)
                record.total_calls = len(activities.filtered(lambda a: 'call' in a.activity_type_id.name.lower()))
                record.total_meetings = len(activities.filtered(lambda a: 'meeting' in a.activity_type_id.name.lower()))
            else:
                record.total_activities = 0
                record.total_calls = 0
                record.total_meetings = 0
    
    @api.depends('date_from', 'date_to', 'employee_id')
    def _compute_customers(self):
        """Tính số khách hàng"""
        for record in self:
            if not record.employee_id:
                record.total_customers = 0
                record.new_customers = 0
                continue
            
            if self.env['ir.model'].search([('model', '=', 'res.partner')]):
                # Tổng khách hàng đang phụ trách
                customers = self.env['res.partner'].search([
                    ('user_id', '=', record.employee_id.user_id.id),
                    ('customer_rank', '>', 0),
                ])
                record.total_customers = len(customers)
                
                # Khách hàng mới trong kỳ
                if record.date_from and record.date_to:
                    new_customers = customers.filtered(
                        lambda c: c.create_date.date() >= record.date_from and 
                                c.create_date.date() <= record.date_to
                    )
                    record.new_customers = len(new_customers)
                else:
                    record.new_customers = 0
            else:
                record.total_customers = 0
                record.new_customers = 0
    
    @api.depends('date_from', 'date_to', 'employee_id')
    def _compute_leads(self):
        """Tính số cơ hội từ CRM"""
        for record in self:
            if not record.date_from or not record.date_to or not record.employee_id:
                record.total_leads = 0
                record.won_leads = 0
                continue
            
            if self.env['ir.model'].search([('model', '=', 'crm.lead')]):
                leads = self.env['crm.lead'].search([
                    ('user_id', '=', record.employee_id.user_id.id),
                    ('create_date', '>=', record.date_from),
                    ('create_date', '<=', record.date_to),
                ])
                record.total_leads = len(leads)
                record.won_leads = len(leads.filtered(lambda l: l.stage_id.is_won))
            else:
                record.total_leads = 0
                record.won_leads = 0
    
    @api.depends('total_leads', 'won_leads')
    def _compute_win_rate(self):
        for record in self:
            if record.total_leads:
                record.win_rate = (record.won_leads / record.total_leads) * 100
            else:
                record.win_rate = 0.0
    
    @api.depends('date_from', 'date_to', 'employee_id')
    def _compute_tasks(self):
        """Tính số công việc từ project.task"""
        for record in self:
            if not record.date_from or not record.date_to or not record.employee_id:
                record.total_tasks = 0
                record.completed_tasks = 0
                record.on_time_tasks = 0
                continue
            
            # Kiểm tra module project có cài không
            if self.env['ir.model'].search([('model', '=', 'project.task')]):
                # Lấy tasks được giao cho nhân viên trong kỳ
                tasks = self.env['project.task'].search([
                    ('user_ids', 'in', [record.employee_id.user_id.id]),
                    '|',
                    ('date_deadline', '>=', record.date_from),
                    ('create_date', '>=', record.date_from),
                    '|',
                    ('date_deadline', '<=', record.date_to),
                    ('create_date', '<=', record.date_to),
                ])
                
                record.total_tasks = len(tasks)
                
                # Công việc hoàn thành
                completed = tasks.filtered(lambda t: t.stage_id.fold == True)
                record.completed_tasks = len(completed)
                
                # Hoàn thành đúng hạn (hoàn thành trước deadline)
                on_time = completed.filtered(
                    lambda t: t.date_deadline and t.write_date.date() <= t.date_deadline
                )
                record.on_time_tasks = len(on_time)
            else:
                record.total_tasks = 0
                record.completed_tasks = 0
                record.on_time_tasks = 0
    
    @api.depends('total_tasks', 'completed_tasks', 'on_time_tasks')
    def _compute_task_rate(self):
        for record in self:
            # Tỷ lệ hoàn thành
            if record.total_tasks:
                record.task_completion_rate = (record.completed_tasks / record.total_tasks) * 100
            else:
                record.task_completion_rate = 0.0
            
            # Tỷ lệ đúng hạn
            if record.completed_tasks:
                record.on_time_rate = (record.on_time_tasks / record.completed_tasks) * 100
            else:
                record.on_time_rate = 0.0
    
    def action_confirm(self):
        self.write({'state': 'confirmed'})
    
    def action_draft(self):
        self.write({'state': 'draft'})
    
    @api.model
    def _cron_create_monthly_performance(self):
        """Tạo đánh giá hiệu suất tự động cho tất cả nhân viên vào đầu tháng"""
        today = fields.Date.today()
        
        # Chỉ chạy vào ngày 1 hàng tháng
        if today.day != 1:
            return
        
        # Lấy tất cả nhân viên đang làm việc
        employees = self.env['hr.employee'].search([('status', '=', 'working')])
        
        for employee in employees:
            # Kiểm tra đã có đánh giá chưa
            existing = self.search([
                ('employee_id', '=', employee.id),
                ('date', '=', today),
            ])
            
            if not existing:
                # Tạo đánh giá hiệu suất mới
                performance = self.create({
                    'employee_id': employee.id,
                    'date': today,
                })
                
                # Tự động confirm để tính toán KPI
                performance.action_confirm()
    
    _sql_constraints = [
        ('employee_date_unique', 'UNIQUE(employee_id, date)', 
         'Đã tồn tại đánh giá hiệu suất cho nhân viên này trong tháng này!'),
    ]
