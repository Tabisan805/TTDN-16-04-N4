# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    # Phân loại khách hàng
    customer_type_btl = fields.Selection([
        ('potential', 'Khách hàng tiềm năng'),
        ('regular', 'Khách hàng chính thức'),
        ('vip', 'Khách hàng VIP'),
        ('inactive', 'Không hoạt động'),
    ], string='Phân loại', default='potential', tracking=True)
    
    # Nguồn khách hàng
    source_btl_id = fields.Many2one('crm.source.btl', string='Nguồn khách hàng')
    
    # Nhân viên phụ trách
    employee_id = fields.Many2one('hr.employee', string='Nhân viên phụ trách', 
                                  compute='_compute_employee_id', store=True,
                                  help='Nhân viên phụ trách khách hàng này')
    employee_name = fields.Char(related='employee_id.name', string='Tên nhân viên')
    employee_phone = fields.Char(related='employee_id.work_phone', string='SĐT nhân viên')
    employee_email = fields.Char(related='employee_id.work_email', string='Email nhân viên')
    employee_department = fields.Char(related='employee_id.department_id.name', string='Phòng ban')
    
    # Thông tin bổ sung
    tax_code = fields.Char(string='Mã số thuế')
    company_size = fields.Selection([
        ('1-10', '1-10 nhân viên'),
        ('11-50', '11-50 nhân viên'),
        ('51-200', '51-200 nhân viên'),
        ('201-500', '201-500 nhân viên'),
        ('500+', 'Trên 500 nhân viên'),
    ], string='Quy mô công ty')
    
    industry_btl = fields.Char(string='Ngành nghề')
    website_url = fields.Char(string='Website')
    
    # Lịch sử tương tác
    interaction_ids = fields.One2many('crm.interaction', 'partner_id', string='Lịch sử tương tác')
    interaction_count = fields.Integer(string='Số lần tương tác', compute='_compute_interaction_statistics')
    last_interaction_date = fields.Datetime(string='Tương tác gần nhất', compute='_compute_interaction_statistics')
    
    # Thống kê tương tác
    total_calls = fields.Integer(string='Số cuộc gọi', compute='_compute_interaction_statistics')
    total_meetings = fields.Integer(string='Số cuộc họp', compute='_compute_interaction_statistics')
    total_emails = fields.Integer(string='Số email', compute='_compute_interaction_statistics')
    total_quotations = fields.Integer(string='Số báo giá', compute='_compute_interaction_statistics')
    
    # Sản phẩm đã mua
    purchased_product_ids = fields.Many2many(
        'product.product', 
        compute='_compute_purchased_products',
        string='Sản phẩm đã mua',
        store=False
    )
    
    # Thống kê mua hàng
    total_orders = fields.Integer(string='Tổng đơn hàng', compute='_compute_purchase_statistics')
    currency_id = fields.Many2one('res.currency', string='Tiền tệ', 
                                  default=lambda self: self.env.company.currency_id)
    total_purchased = fields.Monetary(string='Tổng giá trị mua', compute='_compute_purchase_statistics', currency_field='currency_id')
    average_order_value = fields.Monetary(string='Giá trị đơn TB', compute='_compute_purchase_statistics', currency_field='currency_id')
    last_order_date = fields.Date(string='Đơn hàng gần nhất', compute='_compute_purchase_statistics')
    
    # Đánh giá
    rating = fields.Selection([
        ('1', '⭐'),
        ('2', '⭐⭐'),
        ('3', '⭐⭐⭐'),
        ('4', '⭐⭐⭐⭐'),
        ('5', '⭐⭐⭐⭐⭐'),
    ], string='Đánh giá')
    
    customer_notes = fields.Text(string='Ghi chú đặc biệt')
    
    # Quản lý công nợ - credit_limit đã có sẵn trong account module
    # credit_limit = fields.Monetary(string='Hạn mức công nợ', currency_field='currency_id', default=0.0,
    #                                help='Hạn mức công nợ tối đa cho phép')
    current_debt = fields.Monetary(string='Công nợ hiện tại', compute='_compute_debt', currency_field='currency_id',
                                   help='Tổng công nợ hiện tại của khách hàng')
    debt_percentage = fields.Float(string='Tỷ lệ công nợ (%)', compute='_compute_debt',
                                   help='Tỷ lệ công nợ so với hạn mức')
    overdue_invoices = fields.Integer(string='Hóa đơn quá hạn', compute='_compute_debt')
    
    # Phân tích hành vi mua hàng
    purchase_cycle_days = fields.Integer(string='Chu kỳ mua hàng (ngày)', compute='_compute_purchase_cycle',
                                        help='Số ngày trung bình giữa các lần mua hàng')
    favorite_products = fields.Many2many('product.product', compute='_compute_favorite_products',
                                        string='Sản phẩm yêu thích', 
                                        help='Top 5 sản phẩm mua nhiều nhất')
    last_purchase_days_ago = fields.Integer(string='Ngày từ lần mua cuối', compute='_compute_last_purchase_days')
    is_inactive_customer = fields.Boolean(string='Khách hàng không hoạt động', compute='_compute_last_purchase_days',
                                         help='Không mua hàng > 90 ngày')
    customer_lifetime_value = fields.Monetary(string='CLV', compute='_compute_purchase_statistics',
                                             currency_field='currency_id',
                                             help='Customer Lifetime Value - Tổng giá trị đã mua')
    
    # Xu hướng
    purchase_trend = fields.Selection([
        ('increasing', 'Tăng'),
        ('stable', 'Ổn định'),
        ('decreasing', 'Giảm'),
    ], string='Xu hướng mua hàng', compute='_compute_purchase_trend')
    
    # Nhắc nhở
    payment_reminder_date = fields.Date(string='Ngày nhắc thanh toán')
    payment_reminder_sent = fields.Boolean(string='Đã gửi nhắc nhở', default=False)
    
    @api.depends('user_id')
    def _compute_employee_id(self):
        """Tìm nhân viên dựa trên user_id"""
        for partner in self:
            if partner.user_id:
                employee = self.env['hr.employee'].search([
                    ('user_id', '=', partner.user_id.id)
                ], limit=1)
                partner.employee_id = employee.id if employee else False
            else:
                partner.employee_id = False
    
    @api.depends('interaction_ids')
    def _compute_interaction_statistics(self):
        for partner in self:
            interactions = partner.interaction_ids.filtered(lambda i: i.state == 'done')
            
            partner.interaction_count = len(partner.interaction_ids)
            
            if interactions:
                partner.last_interaction_date = max(interactions.mapped('date'))
            else:
                partner.last_interaction_date = False
            
            # Đếm theo loại
            partner.total_calls = len(interactions.filtered(
                lambda i: 'call' in i.interaction_type_id.code.lower()
            ))
            partner.total_meetings = len(interactions.filtered(
                lambda i: 'meeting' in i.interaction_type_id.code.lower()
            ))
            partner.total_emails = len(interactions.filtered(
                lambda i: 'email' in i.interaction_type_id.code.lower()
            ))
            partner.total_quotations = len(interactions.filtered(
                lambda i: i.quotation_sent
            ))
    
    @api.depends('sale_order_ids')
    def _compute_purchase_statistics(self):
        for partner in self:
            orders = partner.sale_order_ids.filtered(lambda o: o.state in ['sale', 'done'])
            
            partner.total_orders = len(orders)
            partner.total_purchased = sum(orders.mapped('amount_total'))
            partner.customer_lifetime_value = partner.total_purchased  # CLV = Total purchased
            
            if partner.total_orders > 0:
                partner.average_order_value = partner.total_purchased / partner.total_orders
            else:
                partner.average_order_value = 0.0
            
            if orders:
                partner.last_order_date = max(orders.mapped('date_order')).date()
            else:
                partner.last_order_date = False
    
    @api.depends('sale_order_ids.order_line.product_id')
    def _compute_purchased_products(self):
        for partner in self:
            orders = partner.sale_order_ids.filtered(lambda o: o.state in ['sale', 'done'])
            products = orders.mapped('order_line.product_id')
            partner.purchased_product_ids = products
    
    def action_view_interactions(self):
        """Xem tất cả tương tác"""
        return {
            'name': _('Lịch sử tương tác'),
            'type': 'ir.actions.act_window',
            'res_model': 'crm.interaction',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id},
        }
    
    def action_create_interaction(self):
        """Tạo tương tác mới"""
        return {
            'name': _('Tạo tương tác'),
            'type': 'ir.actions.act_window',
            'res_model': 'crm.interaction',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_partner_id': self.id,
                'default_title': f'Tương tác với {self.name}',
            },
        }
    
    def action_view_purchased_products(self):
        """Xem sản phẩm đã mua"""
        return {
            'name': _('Sản phẩm đã mua'),
            'type': 'ir.actions.act_window',
            'res_model': 'product.product',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.purchased_product_ids.ids)],
        }
    
    @api.depends('invoice_ids')
    def _compute_debt(self):
        """Tính công nợ hiện tại"""
        for partner in self:
            # Lấy hóa đơn chưa thanh toán
            unpaid_invoices = self.env['account.move'].search([
                ('partner_id', '=', partner.id),
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('payment_state', 'in', ['not_paid', 'partial'])
            ])
            
            partner.current_debt = sum(unpaid_invoices.mapped('amount_residual'))
            
            # Tỷ lệ công nợ
            if partner.credit_limit > 0:
                partner.debt_percentage = (partner.current_debt / partner.credit_limit) * 100
            else:
                partner.debt_percentage = 0.0
            
            # Hóa đơn quá hạn
            today = fields.Date.today()
            partner.overdue_invoices = len(unpaid_invoices.filtered(
                lambda inv: inv.invoice_date_due and inv.invoice_date_due < today
            ))
    
    @api.depends('sale_order_ids.date_order')
    def _compute_purchase_cycle(self):
        """Tính chu kỳ mua hàng trung bình"""
        for partner in self:
            orders = partner.sale_order_ids.filtered(
                lambda o: o.state in ['sale', 'done']
            ).sorted('date_order')
            
            if len(orders) >= 2:
                # Tính khoảng cách trung bình giữa các đơn hàng
                order_dates = [o.date_order.date() for o in orders]
                intervals = [(order_dates[i+1] - order_dates[i]).days 
                           for i in range(len(order_dates)-1)]
                partner.purchase_cycle_days = int(sum(intervals) / len(intervals))
            else:
                partner.purchase_cycle_days = 0
    
    @api.depends('sale_order_ids.order_line')
    def _compute_favorite_products(self):
        """Tìm top 5 sản phẩm yêu thích"""
        for partner in self:
            orders = partner.sale_order_ids.filtered(lambda o: o.state in ['sale', 'done'])
            
            if orders:
                # Đếm số lượng mua của từng sản phẩm
                product_qty = {}
                for line in orders.mapped('order_line'):
                    if line.product_id.id not in product_qty:
                        product_qty[line.product_id.id] = 0
                    product_qty[line.product_id.id] += line.product_uom_qty
                
                # Lấy top 5
                top_products = sorted(product_qty.items(), key=lambda x: x[1], reverse=True)[:5]
                partner.favorite_products = [(6, 0, [p[0] for p in top_products])]
            else:
                partner.favorite_products = [(5, 0, 0)]
    
    @api.depends('last_order_date')
    def _compute_last_purchase_days(self):
        """Tính số ngày từ lần mua cuối"""
        today = fields.Date.today()
        for partner in self:
            if partner.last_order_date:
                delta = today - partner.last_order_date
                partner.last_purchase_days_ago = delta.days
                partner.is_inactive_customer = delta.days > 90
            else:
                partner.last_purchase_days_ago = 0
                partner.is_inactive_customer = False
    
    @api.depends('sale_order_ids.amount_total')
    def _compute_purchase_trend(self):
        """Phân tích xu hướng mua hàng"""
        for partner in self:
            orders = partner.sale_order_ids.filtered(
                lambda o: o.state in ['sale', 'done']
            ).sorted('date_order')
            
            if len(orders) >= 3:
                # So sánh 3 đơn gần nhất với 3 đơn trước đó
                recent_orders = orders[-3:]
                previous_orders = orders[-6:-3] if len(orders) >= 6 else orders[:-3]
                
                recent_avg = sum(recent_orders.mapped('amount_total')) / len(recent_orders)
                previous_avg = sum(previous_orders.mapped('amount_total')) / len(previous_orders) if previous_orders else 0
                
                if recent_avg > previous_avg * 1.1:
                    partner.purchase_trend = 'increasing'
                elif recent_avg < previous_avg * 0.9:
                    partner.purchase_trend = 'decreasing'
                else:
                    partner.purchase_trend = 'stable'
            else:
                partner.purchase_trend = 'stable'
    
    def action_send_payment_reminder(self):
        """Gửi nhắc nhở thanh toán"""
        self.ensure_one()
        
        if self.current_debt > 0:
            # TODO: Implement email template
            self.payment_reminder_sent = True
            self.payment_reminder_date = fields.Date.today()
            
            self.message_post(
                body=f"Đã gửi nhắc nhở thanh toán. Công nợ hiện tại: {self.current_debt:,.0f} {self.currency_id.symbol}",
                subject='Nhắc nhở thanh toán'
            )
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': 'Đã gửi email nhắc nhở thanh toán',
                    'type': 'success',
                    'sticky': False,
                }
            }
    
    @api.model
    def _cron_send_payment_reminders(self):
        """Cron job: Gửi nhắc nhở thanh toán tự động cho khách có công nợ"""
        today = fields.Date.today()
        
        # Tìm khách hàng có công nợ và chưa gửi nhắc nhở trong 7 ngày
        partners = self.search([
            ('customer_rank', '>', 0),
            ('current_debt', '>', 0),
            '|',
            ('payment_reminder_date', '=', False),
            ('payment_reminder_date', '<', fields.Date.add(today, days=-7))
        ])
        
        for partner in partners:
            if partner.overdue_invoices > 0:
                partner.action_send_payment_reminder()
    
    @api.model
    def _cron_check_inactive_customers(self):
        """Cron job: Cảnh báo khách hàng không hoạt động (>90 ngày không mua)"""
        inactive_customers = self.search([
            ('customer_rank', '>', 0),
            ('is_inactive_customer', '=', True),
            ('user_id', '!=', False)
        ])
        
        for customer in inactive_customers:
            # Gửi thông báo cho sale phụ trách
            if customer.user_id:
                customer.message_post(
                    body=f'''Cảnh báo: Khách hàng {customer.name} không mua hàng trong {customer.last_purchase_days_ago} ngày. 
                          Vui lòng liên hệ chăm sóc khách hàng.''',
                    subject='Cảnh báo khách hàng không hoạt động',
                    partner_ids=[customer.user_id.partner_id.id]
                )
