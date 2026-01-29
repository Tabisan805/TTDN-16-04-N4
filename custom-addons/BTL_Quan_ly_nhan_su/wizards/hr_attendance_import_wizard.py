# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
import io
import csv
from datetime import datetime


class HrAttendanceImportWizard(models.TransientModel):
    _name = 'hr.attendance.import.wizard'
    _description = 'Wizard import dữ liệu chấm công'
    
    file_data = fields.Binary(string='File CSV', required=True)
    file_name = fields.Char(string='Tên file')
    
    def action_import(self):
        """Import dữ liệu chấm công từ CSV"""
        if not self.file_data:
            raise UserError(_('Vui lòng chọn file!'))
        
        # Đọc file CSV
        file_content = base64.b64decode(self.file_data)
        csv_data = io.StringIO(file_content.decode('utf-8'))
        csv_reader = csv.DictReader(csv_data)
        
        attendances = self.env['hr.attendance.btl']
        errors = []
        success_count = 0
        
        for row_num, row in enumerate(csv_reader, 2):
            try:
                # Tìm nhân viên theo mã
                employee_code = row.get('employee_code', '').strip()
                employee = self.env['hr.employee'].search([('employee_code', '=', employee_code)], limit=1)
                
                if not employee:
                    errors.append(f"Dòng {row_num}: Không tìm thấy nhân viên: {employee_code}")
                    continue
                
                # Parse ngày giờ
                date_str = row.get('date', '').strip()
                check_in_str = row.get('check_in', '').strip()
                check_out_str = row.get('check_out', '').strip()
                
                if not date_str or not check_in_str:
                    errors.append(f"Dòng {row_num}: Thiếu ngày hoặc giờ vào")
                    continue
                
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
                check_in = datetime.strptime(f"{date_str} {check_in_str}", '%Y-%m-%d %H:%M')
                check_out = datetime.strptime(f"{date_str} {check_out_str}", '%Y-%m-%d %H:%M') if check_out_str else False
                
                # Lấy các trường bổ sung từ file
                department_id = False
                department_name = row.get('department', '').strip()
                if department_name:
                    dept = self.env['hr.department'].search([('name', 'ilike', department_name)], limit=1)
                    department_id = dept.id if dept else False
                
                # Tính giờ làm việc nếu có check_out
                working_hours = 0
                if check_out:
                    time_diff = check_out - check_in
                    working_hours = time_diff.total_seconds() / 3600
                
                # Dữ liệu bổ sung (nếu có)
                overtime_hours = 0
                try:
                    overtime_hours = float(row.get('overtime_hours', 0))
                except (ValueError, TypeError):
                    overtime_hours = 0
                
                # Xác định trạng thái
                status = row.get('status', 'confirmed').strip().lower()
                if status not in ['draft', 'confirmed', 'approved']:
                    status = 'confirmed'
                
                # Tạo bản ghi chấm công với TẤT CẢ thông tin tự động
                attendance_data = {
                    'employee_id': employee.id,
                    'date': date,
                    'check_in': check_in,
                    'check_out': check_out,
                    'state': status,
                    'working_hours': working_hours,
                }
                
                # Thêm thông tin bổ sung nếu model có
                if department_id:
                    if 'department_id' in self.env['hr.attendance.btl']._fields:
                        attendance_data['department_id'] = department_id
                
                if overtime_hours > 0:
                    if 'overtime_hours' in self.env['hr.attendance.btl']._fields:
                        attendance_data['overtime_hours'] = overtime_hours
                
                # Lấy note nếu có
                note = row.get('note', '').strip()
                if note and 'note' in self.env['hr.attendance.btl']._fields:
                    attendance_data['note'] = note
                
                attendance = attendances.create(attendance_data)
                attendances |= attendance
                success_count += 1
                
            except ValueError as ve:
                errors.append(f"Dòng {row_num}: Lỗi định dạng dữ liệu - {str(ve)}")
            except Exception as e:
                errors.append(f"Dòng {row_num}: {str(e)}")
        
        # Tạo message thành công/lỗi
        message = f"✓ Đã import thành công {success_count} bản ghi chấm công"
        if errors:
            message += f"\n\n⚠ {len(errors)} lỗi xảy ra:\n" + '\n'.join(errors[:10])
            if len(errors) > 10:
                message += f"\n... và {len(errors) - 10} lỗi khác"
        
        if success_count == 0:
            raise UserError(_(message))
        
        # Thông báo kết quả
        self.env.user.notify_info(message)
        
        return {
            'name': _('Chấm công đã import'),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.attendance.btl',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', attendances.ids)],
        }
