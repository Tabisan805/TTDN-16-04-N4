# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class CrmInteraction(models.Model):
    _name = 'crm.interaction'
    _description = 'Lịch sử tương tác khách hàng'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'
    _rec_name = 'title'
    
    title = fields.Char(string='Tiêu đề', required=True)
    
    # Khách hàng
    partner_id = fields.Many2one('res.partner', string='Khách hàng', required=True, ondelete='cascade')
    lead_id = fields.Many2one('crm.lead', string='Cơ hội', ondelete='set null')
    
    # Loại tương tác
    interaction_type_id = fields.Many2one('crm.interaction.type', string='Loại tương tác', required=True)
    
    # Thời gian
    date = fields.Datetime(string='Ngày giờ', required=True, default=fields.Datetime.now)
    duration = fields.Float(string='Thời lượng (phút)')
    
    # Người thực hiện
    user_id = fields.Many2one('res.users', string='Người thực hiện', default=lambda self: self.env.user, required=True)
    
    # Nội dung
    description = fields.Html(string='Nội dung chi tiết')
    note = fields.Text(string='Ghi chú')
    
    # Kết quả
    outcome = fields.Selection([
        ('successful', 'Thành công'),
        ('failed', 'Không thành công'),
        ('pending', 'Đang chờ'),
        ('scheduled', 'Đã lên lịch'),
    ], string='Kết quả', default='successful')
    
    # Lịch hẹn tiếp theo
    next_action_date = fields.Datetime(string='Lịch hẹn tiếp theo')
    next_action_note = fields.Text(string='Ghi chú lịch hẹn')
    
    # File đính kèm
    attachment_ids = fields.Many2many('ir.attachment', string='File đính kèm')
    
    # Liên kết
    sale_order_id = fields.Many2one('sale.order', string='Đơn hàng', ondelete='set null')
    quotation_sent = fields.Boolean(string='Đã gửi báo giá')
    
    # Trạng thái
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('done', 'Hoàn thành'),
        ('cancelled', 'Đã hủy'),
    ], string='Trạng thái', default='draft', required=True)
    
    # Liên kết task
    task_id = fields.Many2one('project.task', string='Công việc follow-up', readonly=True)
    auto_create_task = fields.Boolean(string='Tự động tạo công việc', default=True,
                                      help='Tự động tạo công việc follow-up khi hoàn thành')
    
    def action_done(self):
        """Hoàn thành tương tác và tạo task follow-up nếu cần"""
        self.write({'state': 'done'})
        
        # Tự động tạo task follow-up nếu có lịch hẹn tiếp theo
        for interaction in self:
            if interaction.auto_create_task and interaction.next_action_date and not interaction.task_id:
                interaction._create_followup_task()
    
    def action_cancel(self):
        self.write({'state': 'cancelled'})
    
    def action_draft(self):
        self.write({'state': 'draft'})
    
    def _create_followup_task(self):
        """Tạo công việc follow-up tự động"""
        self.ensure_one()
        
        # Kiểm tra module công việc có được cài đặt không
        if not self.env['ir.module.module'].search([
            ('name', '=', 'BTL_Quan_ly_cong_viec'),
            ('state', '=', 'installed')
        ], limit=1):
            return
        
        # Tạo task
        task_vals = {
            'name': f'Follow-up: {self.title}',
            'description': f'''
<p><strong>Follow-up từ tương tác:</strong> {self.title}</p>
<p><strong>Khách hàng:</strong> {self.partner_id.name}</p>
<p><strong>Nội dung tương tác trước:</strong></p>
{self.description or ''}
<p><strong>Ghi chú lịch hẹn:</strong></p>
{self.next_action_note or ''}
            ''',
            'user_id': self.user_id.id,
            'date_deadline': self.next_action_date,
            'partner_id': self.partner_id.id,
            'lead_id': self.lead_id.id if self.lead_id else False,
        }
        
        try:
            task = self.env['project.task'].create(task_vals)
            self.task_id = task.id
            
            self.message_post(
                body=f'Đã tạo công việc follow-up: <a href="#id={task.id}&model=project.task">{task.name}</a>',
                subject='Tạo công việc tự động'
            )
        except Exception as e:
            # Nếu không tạo được task (module chưa cài hoặc lỗi), bỏ qua
            pass
    
    @api.model_create_multi
    def create(self, vals_list):
        """Override create để tự động tạo task khi tạo từ lead"""
        records = super().create(vals_list)
        
        for record in records:
            # Nếu tạo từ lead, tạo task tự động
            if record.lead_id and record.state == 'done' and record.auto_create_task:
                record._create_followup_task()
        
        return records
    
    @api.model
    def _cron_send_next_action_reminders(self):
        """Cron job: Nhắc nhở lịch hẹn tương tác sắp tới"""
        today = fields.Datetime.now()
        tomorrow = fields.Datetime.add(today, days=1)
        
        # Tìm tương tác có lịch hẹn trong 24h tới
        interactions = self.search([
            ('next_action_date', '>=', today),
            ('next_action_date', '<=', tomorrow),
            ('state', '=', 'done'),
            ('user_id', '!=', False)
        ])
        
        for interaction in interactions:
            interaction.message_post(
                body=f'''Nhắc nhở: Bạn có lịch hẹn với khách hàng {interaction.partner_id.name} 
                      vào {interaction.next_action_date.strftime('%d/%m/%Y %H:%M')}. 
                      Nội dung: {interaction.next_action_note or 'Chưa có ghi chú'}''',
                subject='Nhắc nhở lịch hẹn',
                partner_ids=[interaction.user_id.partner_id.id]
            )
