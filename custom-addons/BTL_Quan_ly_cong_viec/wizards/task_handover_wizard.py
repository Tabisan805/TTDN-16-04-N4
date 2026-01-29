# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class TaskHandoverWizard(models.TransientModel):
    _name = 'task.handover.wizard'
    _description = 'Task Handover Wizard'
    
    task_id = fields.Many2one('project.task', string='Công việc', required=True)
    from_user_id = fields.Many2one('res.users', string='Người bàn giao', required=True)
    to_user_id = fields.Many2one('res.users', string='Người nhận', required=True)
    handover_date = fields.Datetime(string='Ngày bàn giao', default=fields.Datetime.now, required=True)
    notes = fields.Text(string='Ghi chú')
    
    # Các field bổ sung để import tự động
    priority_level = fields.Selection([
        ('low', 'Thấp'),
        ('normal', 'Bình thường'),
        ('high', 'Cao'),
        ('urgent', 'Khẩn cấp'),
    ], string='Mức độ ưu tiên', help='Cập nhật mức độ ưu tiên cho công việc')
    
    task_type_code = fields.Selection([
        ('sale', 'Sale - Bán hàng'),
        ('marketing', 'Marketing'),
        ('accounting', 'Kế toán'),
        ('hr', 'Nhân sự'),
        ('assistant', 'Trợ lý'),
    ], string='Loại công việc', help='Cập nhật loại công việc')
    
    update_status = fields.Boolean(string='Cập nhật trạng thái', default=True,
                                  help='Tự động cập nhật trạng thái công việc thành "in_progress"')
    
    @api.model
    def default_get(self, fields_list):
        res = super(TaskHandoverWizard, self).default_get(fields_list)
        if self.env.context.get('active_model') == 'project.task' and self.env.context.get('active_id'):
            task = self.env['project.task'].browse(self.env.context['active_id'])
            res.update({
                'task_id': task.id,
                'from_user_id': task.user_ids[0].id if task.user_ids else False,
                'priority_level': task.priority_level if hasattr(task, 'priority_level') else 'normal',
                'task_type_code': task.task_type_code if hasattr(task, 'task_type_code') else 'sale',
            })
        return res
    
    def action_handover(self):
        """Thực hiện bàn giao công việc"""
        self.ensure_one()
        
        if not self.to_user_id:
            raise UserError(_('Vui lòng chọn người nhận bàn giao!'))
        
        if self.from_user_id == self.to_user_id:
            raise UserError(_('Người bàn giao và người nhận không thể giống nhau!'))
        
        # Tạo bản ghi bàn giao
        handover = self.env['task.handover.btl'].create({
            'task_id': self.task_id.id,
            'from_user_id': self.from_user_id.id,
            'to_user_id': self.to_user_id.id,
            'handover_date': self.handover_date,
            'notes': self.notes,
            'state': 'pending',
        })
        
        # Chuẩn bị dữ liệu cập nhật công việc
        task_update_data = {
            'user_ids': [(6, 0, [self.to_user_id.id])],
        }
        
        # Tự động cập nhật các field nếu được chỉ định
        if self.priority_level:
            task_update_data['priority_level'] = self.priority_level
        
        if self.task_type_code:
            task_update_data['task_type_code'] = self.task_type_code
        
        if self.update_status:
            task_update_data['task_status'] = 'in_progress'
        
        # Cập nhật người phụ trách công việc và các field khác
        self.task_id.write(task_update_data)
        
        # Gửi thông báo
        message_body = _('Công việc đã được bàn giao từ %s đến %s') % (
            self.from_user_id.name, 
            self.to_user_id.name
        )
        
        if self.notes:
            message_body += f"\n\nGhi chú: {self.notes}"
        
        self.task_id.message_post(
            body=message_body,
            subtype_xmlid='mail.mt_note',
        )
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'task.handover.btl',
            'res_id': handover.id,
            'view_mode': 'form',
            'target': 'current',
        }
