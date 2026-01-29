# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
import io
import csv
from datetime import datetime


class HrEmployeeImportWizard(models.TransientModel):
    _name = 'hr.employee.import.wizard'
    _description = 'Wizard import dữ liệu nhân viên'
    
    file_data = fields.Binary(string='File CSV', required=True)
    file_name = fields.Char(string='Tên file')
    skip_existing = fields.Boolean(string='Bỏ qua nhân viên đã tồn tại', default=True,
                                   help='Nếu bật, sẽ bỏ qua nhân viên có cùng mã/email')
    
    def action_import(self):
        """Import dữ liệu nhân viên từ CSV"""
        if not self.file_data:
            raise UserError(_('Vui lòng chọn file!'))
        
        # Đọc file CSV
        file_content = base64.b64decode(self.file_data)
        csv_data = io.StringIO(file_content.decode('utf-8'))
        csv_reader = csv.DictReader(csv_data)
        
        employees = self.env['hr.employee']
        errors = []
        success_count = 0
        
        for row_num, row in enumerate(csv_reader, 2):
            try:
                # Lấy dữ liệu bắt buộc
                name = row.get('name', '').strip()
                work_email = row.get('work_email', '').strip()
                
                if not name or not work_email:
                    errors.append(f"Dòng {row_num}: Thiếu tên hoặc email")
                    continue
                
                # Kiểm tra trùng lặp
                if self.skip_existing:
                    existing = self.env['hr.employee'].search([
                        '|',
                        ('name', '=', name),
                        ('work_email', '=', work_email)
                    ], limit=1)
                    if existing:
                        errors.append(f"Dòng {row_num}: Nhân viên '{name}' đã tồn tại, bỏ qua")
                        continue
                
                # Xây dựng dữ liệu nhân viên
                employee_data = {
                    'name': name,
                    'work_email': work_email,
                }
                
                # Thêm các field tùy chọn nếu có
                if row.get('work_phone'):
                    employee_data['work_phone'] = row.get('work_phone', '').strip()
                
                if row.get('gender'):
                    gender = row.get('gender', '').strip().lower()
                    if gender in ['male', 'female', 'other']:
                        employee_data['gender'] = gender
                
                # Department
                if row.get('department'):
                    dept_name = row.get('department', '').strip()
                    dept = self.env['hr.department'].search([('name', 'ilike', dept_name)], limit=1)
                    if dept:
                        employee_data['department_id'] = dept.id
                
                # Job
                if row.get('job_title'):
                    job_name = row.get('job_title', '').strip()
                    job = self.env['hr.job'].search([('name', 'ilike', job_name)], limit=1)
                    if job:
                        employee_data['job_id'] = job.id
                
                # Birthday
                if row.get('birthday'):
                    try:
                        birthday = datetime.strptime(row.get('birthday').strip(), '%Y-%m-%d').date()
                        employee_data['birthday'] = birthday
                    except:
                        pass
                
                # Lương
                if row.get('basic_wage'):
                    try:
                        employee_data['basic_wage'] = float(row.get('basic_wage'))
                    except:
                        pass
                
                if row.get('wage_type'):
                    wage_type = row.get('wage_type', '').strip().lower()
                    if wage_type in ['monthly', 'daily', 'hourly']:
                        employee_data['wage_type'] = wage_type
                
                # Commission
                if row.get('has_commission'):
                    has_comm = row.get('has_commission', '').strip().lower()
                    employee_data['has_commission'] = has_comm in ['true', '1', 'yes']
                
                if row.get('commission_rate'):
                    try:
                        employee_data['commission_rate'] = float(row.get('commission_rate'))
                    except:
                        pass
                
                # Status
                if row.get('status'):
                    status = row.get('status', '').strip().lower()
                    if status in ['working', 'resigned', 'suspended']:
                        employee_data['status'] = status
                
                # Join date
                if row.get('join_date'):
                    try:
                        join_date = datetime.strptime(row.get('join_date').strip(), '%Y-%m-%d').date()
                        employee_data['join_date'] = join_date
                    except:
                        pass
                
                # Tạo nhân viên - KHÔNG dùng external ID để tránh xung đột
                employee = self.env['hr.employee'].create(employee_data)
                employees |= employee
                success_count += 1
                
            except Exception as e:
                errors.append(f"Dòng {row_num}: {str(e)}")
        
        # Tạo message thành công/lỗi
        message = f"✓ Đã import thành công {success_count} nhân viên"
        if errors:
            message += f"\n\n⚠ {len(errors)} lỗi xảy ra:\n" + '\n'.join(errors[:15])
            if len(errors) > 15:
                message += f"\n... và {len(errors) - 15} lỗi khác"
        
        if success_count == 0:
            raise UserError(_(message))
        
        return {
            'name': _('Nhân viên đã import'),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', employees.ids)] if employees else [],
        }
