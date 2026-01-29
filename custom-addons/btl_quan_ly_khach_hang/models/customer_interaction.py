# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class CustomerInteraction(models.Model):
    _name = 'customer.interaction.btl'
    _description = 'Tương tác khách hàng BTL'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'interaction_date desc'

    name = fields.Char(
        string='Tiêu đề',
        required=True,
        tracking=True
    )
    interaction_type = fields.Selection([
        ('call', 'Cuộc gọi'),
        ('email', 'Email'),
        ('meeting', 'Cuộc họp'),
        ('quotation', 'Gửi báo giá'),
        ('other', 'Khác')
    ], string='Loại tương tác', required=True, default='call', tracking=True)
    
    interaction_date = fields.Datetime(
        string='Thời gian tương tác',
        required=True,
        default=fields.Datetime.now,
        tracking=True
    )
    duration = fields.Float(
        string='Thời lượng (phút)',
        help='Thời gian tương tác tính bằng phút'
    )
    
    # Relations
    lead_id = fields.Many2one(
        'crm.lead',
        string='Lead/Cơ hội',
        ondelete='cascade',
        index=True
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Khách hàng',
        ondelete='cascade',
        index=True
    )
    user_id = fields.Many2one(
        'res.users',
        string='Người thực hiện',
        required=True,
        default=lambda self: self.env.user,
        tracking=True
    )
    
    # Content
    description = fields.Html(
        string='Nội dung chi tiết',
        help='Mô tả chi tiết nội dung tương tác'
    )
    result = fields.Text(
        string='Kết quả',
        help='Kết quả của tương tác này',
        tracking=True
    )
    
    # State
    state = fields.Selection([
        ('scheduled', 'Đã lên lịch'),
        ('in_progress', 'Đang thực hiện'),
        ('completed', 'Hoàn thành'),
        ('cancelled', 'Đã hủy')
    ], string='Trạng thái', default='scheduled', required=True, tracking=True)
    
    # Related fields
    partner_phone = fields.Char(
        related='partner_id.phone',
        string='Số điện thoại',
        readonly=True
    )
    partner_email = fields.Char(
        related='partner_id.email',
        string='Email',
        readonly=True
    )
    
    # Follow-up
    create_task = fields.Boolean(
        string='Tạo công việc follow-up',
        default=True,
        help='Tự động tạo task follow-up sau tương tác'
    )
    task_id = fields.Many2one(
        'project.task',
        string='Công việc liên quan',
        readonly=True
    )
    
    @api.onchange('lead_id')
    def _onchange_lead_id(self):
        """Tự động điền partner từ lead"""
        if self.lead_id and self.lead_id.partner_id:
            self.partner_id = self.lead_id.partner_id
    
    def action_start(self):
        """Bắt đầu tương tác"""
        self.ensure_one()
        if self.state != 'scheduled':
            raise UserError('Chỉ có thể bắt đầu tương tác đã lên lịch!')
        self.write({
            'state': 'in_progress',
            'interaction_date': fields.Datetime.now()
        })
    
    def action_complete(self):
        """Hoàn thành tương tác"""
        self.ensure_one()
        if self.state == 'completed':
            raise UserError('Tương tác đã được hoàn thành!')
        
        self.write({'state': 'completed'})
        
        # Create follow-up task if needed
        if self.create_task and not self.task_id:
            self._create_followup_task()
        
        # Log message
        self.message_post(
            body=f"Tương tác hoàn thành. Kết quả: {self.result or 'Không có'}"
        )
    
    def action_cancel(self):
        """Hủy tương tác"""
        self.ensure_one()
        if self.state == 'completed':
            raise UserError('Không thể hủy tương tác đã hoàn thành!')
        self.write({'state': 'cancelled'})
    
    def _create_followup_task(self):
        """Tạo task follow-up sau tương tác"""
        self.ensure_one()
        
        # Check if BTL_Quan_ly_cong_viec module is installed
        if 'project.task' not in self.env:
            return
        
        task_vals = {
            'name': f'Follow-up: {self.name}',
            'description': f'''
                <p>Follow-up sau tương tác:</p>
                <ul>
                    <li>Loại: {dict(self._fields['interaction_type'].selection).get(self.interaction_type)}</li>
                    <li>Khách hàng: {self.partner_id.name if self.partner_id else self.lead_id.name}</li>
                    <li>Kết quả: {self.result or 'Không có'}</li>
                </ul>
            ''',
            'user_ids': [(6, 0, [self.user_id.id])],
            'partner_id': self.partner_id.id if self.partner_id else False,
        }
        
        # Add BTL specific fields if available
        if hasattr(self.env['project.task'], 'task_type_code'):
            task_vals['task_type_code'] = 'sale'
            task_vals['priority_level'] = 'normal'
        
        task = self.env['project.task'].create(task_vals)
        self.task_id = task.id
        
        return task
