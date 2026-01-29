# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    # Liên kết với tương tác
    interaction_ids = fields.One2many('crm.interaction', 'sale_order_id', string='Lịch sử tương tác')
    interaction_count = fields.Integer(string='Số tương tác', compute='_compute_interaction_count')
    
    @api.depends('interaction_ids')
    def _compute_interaction_count(self):
        for order in self:
            order.interaction_count = len(order.interaction_ids)
    
    def action_view_interactions(self):
        """Xem tương tác liên quan đến đơn hàng"""
        return {
            'name': 'Lịch sử tương tác',
            'type': 'ir.actions.act_window',
            'res_model': 'crm.interaction',
            'view_mode': 'tree,form',
            'domain': [('sale_order_id', '=', self.id)],
            'context': {
                'default_sale_order_id': self.id,
                'default_partner_id': self.partner_id.id,
            },
        }
