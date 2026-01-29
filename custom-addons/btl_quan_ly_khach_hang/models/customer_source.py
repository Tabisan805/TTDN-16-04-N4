# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CustomerSource(models.Model):
    _name = 'customer.source.btl'
    _description = 'Nguồn khách hàng BTL'
    _order = 'name'

    name = fields.Char(
        string='Tên nguồn',
        required=True,
        translate=True
    )
    code = fields.Char(
        string='Mã nguồn',
        required=True,
        copy=False
    )
    description = fields.Text(
        string='Mô tả'
    )
    active = fields.Boolean(
        string='Hoạt động',
        default=True
    )
    
    # Statistics
    lead_count = fields.Integer(
        string='Số Lead',
        compute='_compute_statistics',
        store=False
    )
    conversion_rate = fields.Float(
        string='Tỷ lệ chuyển đổi (%)',
        compute='_compute_statistics',
        store=False
    )
    total_revenue = fields.Monetary(
        string='Tổng doanh thu',
        compute='_compute_statistics',
        currency_field='currency_id',
        store=False
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Tiền tệ',
        default=lambda self: self.env.company.currency_id
    )
    
    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Mã nguồn phải là duy nhất!')
    ]
    
    @api.depends()
    def _compute_statistics(self):
        """Tính toán thống kê nguồn khách hàng"""
        for record in self:
            # Count leads from this source
            leads = self.env['crm.lead'].search([
                ('source_id', '=', record.id)
            ])
            record.lead_count = len(leads)
            
            # Calculate conversion rate
            won_leads = leads.filtered(lambda l: l.probability == 100)
            if record.lead_count > 0:
                record.conversion_rate = (len(won_leads) / record.lead_count) * 100
            else:
                record.conversion_rate = 0
            
            # Calculate total revenue
            record.total_revenue = sum(won_leads.mapped('expected_revenue'))
    
    def action_view_leads(self):
        """Xem danh sách lead từ nguồn này"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Lead từ {self.name}',
            'res_model': 'crm.lead',
            'view_mode': 'list,form,kanban',
            'domain': [('source_id', '=', self.id)],
            'context': {'default_source_id': self.id}
        }
