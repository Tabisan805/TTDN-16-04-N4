# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CrmSource(models.Model):
    _name = 'crm.source.btl'
    _description = 'Nguồn khách hàng'
    _order = 'sequence, name'
    
    name = fields.Char(string='Tên nguồn', required=True)
    code = fields.Char(string='Mã', required=True)
    sequence = fields.Integer(string='Thứ tự', default=10)
    active = fields.Boolean(string='Hoạt động', default=True)
    color = fields.Integer(string='Màu sắc')
    
    # Thống kê
    lead_count = fields.Integer(string='Số leads', compute='_compute_statistics')
    customer_count = fields.Integer(string='Số khách hàng', compute='_compute_statistics')
    conversion_rate = fields.Float(string='Tỷ lệ chuyển đổi (%)', compute='_compute_statistics')
    
    description = fields.Text(string='Mô tả')
    
    @api.depends('name')
    def _compute_statistics(self):
        for source in self:
            # Đếm leads
            leads = self.env['crm.lead'].search([('source_btl_id', '=', source.id)])
            source.lead_count = len(leads)
            
            # Đếm customers (leads đã chuyển đổi)
            customers = leads.filtered(lambda l: l.type == 'opportunity' and l.stage_id.is_won)
            source.customer_count = len(customers)
            
            # Tỷ lệ chuyển đổi
            if source.lead_count > 0:
                source.conversion_rate = (source.customer_count / source.lead_count) * 100
            else:
                source.conversion_rate = 0.0
    
    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'Mã nguồn khách hàng đã tồn tại!'),
    ]
