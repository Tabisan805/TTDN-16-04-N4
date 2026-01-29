# -*- coding: utf-8 -*-
from odoo import models, fields


class TaskHandoverStage(models.Model):
    """Model để định nghĩa các stage cho công việc bàn giao"""
    _name = 'task.handover.stage'
    _description = 'Task Handover Stage'
    _order = 'sequence, id'

    name = fields.Char('Stage Name', required=True, translate=True)
    description = fields.Text('Description', translate=True)
    sequence = fields.Integer('Sequence', default=10)
    color = fields.Integer('Color', default=0)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ], string='State', required=True, default='draft')
    active = fields.Boolean('Active', default=True)

    _sql_constraints = [
        ('state_unique', 'unique(state)', 'State value must be unique!'),
    ]
