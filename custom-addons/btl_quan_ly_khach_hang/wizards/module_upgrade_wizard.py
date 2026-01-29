# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ModuleUpgradeWizard(models.TransientModel):
    _name = 'module.upgrade.wizard'
    _description = 'Wizard Update Modules'
    
    upgrade_type = fields.Selection([
        ('all', 'Update tất cả modules'),
        ('custom', 'Update custom modules (BTL)'),
        ('specific', 'Update module cụ thể'),
    ], string='Kiểu update', default='all', required=True)
    
    module_ids = fields.Many2many('ir.module.module', string='Chọn modules',
                                   help='Chỉ sử dụng khi chọn "Update module cụ thể"')
    
    show_progress = fields.Boolean(string='Hiển thị tiến độ', default=True)
    
    @api.onchange('upgrade_type')
    def _onchange_upgrade_type(self):
        """Tự động set modules dựa vào loại update"""
        if self.upgrade_type == 'custom':
            # Lấy tất cả custom modules (bắt đầu bằng BTL)
            custom_modules = self.env['ir.module.module'].search([
                ('name', 'like', 'BTL'),
                ('state', '=', 'installed')
            ])
            self.module_ids = custom_modules
        elif self.upgrade_type == 'all':
            # Lấy tất cả modules installed
            all_modules = self.env['ir.module.module'].search([
                ('state', '=', 'installed')
            ])
            self.module_ids = all_modules
    
    def action_upgrade(self):
        """Thực hiện upgrade modules"""
        self.ensure_one()
        
        if self.upgrade_type == 'all':
            modules = self.env['ir.module.module'].search([
                ('state', '=', 'installed')
            ])
            module_names = ', '.join([m.name for m in modules])
            message = f"Đang update {len(modules)} modules: {module_names[:100]}..."
        
        elif self.upgrade_type == 'custom':
            modules = self.env['ir.module.module'].search([
                ('name', 'like', 'BTL'),
                ('state', '=', 'installed')
            ])
            module_names = ', '.join([m.name for m in modules])
            message = f"Đang update {len(modules)} custom modules: {module_names}"
        
        elif self.upgrade_type == 'specific':
            modules = self.module_ids
            if not modules:
                raise UserError(_('Vui lòng chọn ít nhất 1 module!'))
            module_names = ', '.join([m.name for m in modules])
            message = f"Đang update {len(modules)} modules: {module_names}"
        
        if not modules:
            raise UserError(_('Không có modules để update!'))
        
        # Mark modules for upgrade
        modules.write({'state': 'to upgrade'})
        
        # Trigger upgrade via module upgrade action
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }


class ModuleUpgradeButton(models.Model):
    """Mixin để thêm button upgrade vào models"""
    _name = 'module.upgrade.mixin'
    _description = 'Mixin Update Module'
    
    @api.model
    def get_module_update_action(self):
        """Return action để mở wizard"""
        return {
            'name': _('Update Modules'),
            'type': 'ir.actions.act_window',
            'res_model': 'module.upgrade.wizard',
            'view_mode': 'form',
            'target': 'new',
        }
