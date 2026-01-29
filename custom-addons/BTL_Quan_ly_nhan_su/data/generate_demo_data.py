#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script generate demo data cho BTL_Quan_ly_nhan_su
Tạo 150 records: 60 attendance + 45 leave + 45 overtime
"""

from datetime import datetime, timedelta
import random

# Generate 60 attendance records (30 ngày gần nhất cho 2 nhân viên ngẫu nhiên mỗi ngày)
def generate_attendance_data():
    xml_records = []
    today = datetime.now()
    
    for day_offset in range(30):
        date = today - timedelta(days=day_offset)
        
        # 2 nhân viên chấm công mỗi ngày
        for emp_num in random.sample(range(1, 51), 2):
            record_id = f"attendance_demo_{len(xml_records)+1:03d}"
            emp_ref = f"employee_demo_{emp_num:03d}"
            
            # Random giờ vào (7:30 - 8:30)
            check_in_hour = random.randint(7, 8)
            check_in_minute = random.randint(0, 59)
            check_in = date.replace(hour=check_in_hour, minute=check_in_minute, second=0)
            
            # Giờ ra (17:00 - 18:30)
            check_out_hour = random.randint(17, 18)
            check_out_minute = random.randint(0, 59)
            check_out = date.replace(hour=check_out_hour, minute=check_out_minute, second=0)
            
            state = random.choice(['draft', 'confirmed', 'validated'])
            
            xml = f'''        <record id="{record_id}" model="hr.attendance.btl">
            <field name="employee_id" ref="{emp_ref}"/>
            <field name="date" eval="(DateTime.now() - timedelta(days={day_offset})).strftime('%Y-%m-%d')"/>
            <field name="check_in" eval="(DateTime.now() - timedelta(days={day_offset})).replace(hour={check_in_hour}, minute={check_in_minute}, second=0)"/>
            <field name="check_out" eval="(DateTime.now() - timedelta(days={day_offset})).replace(hour={check_out_hour}, minute={check_out_minute}, second=0)"/>
            <field name="state">{state}</field>
        </record>
'''
            xml_records.append(xml)
    
    return xml_records

# Generate 45 leave records
def generate_leave_data():
    xml_records = []
    leave_types = ['annual', 'sick', 'unpaid', 'maternity', 'other']
    
    for i in range(45):
        record_id = f"leave_demo_{i+1:03d}"
        emp_num = random.randint(1, 50)
        emp_ref = f"employee_demo_{emp_num:03d}"
        
        # Random ngày nghỉ trong 90 ngày qua
        day_offset = random.randint(0, 90)
        num_days = random.choice([1, 2, 3, 5, 7])
        
        leave_type = random.choice(leave_types)
        state = random.choice(['draft', 'confirmed', 'approved', 'refused'])
        
        xml = f'''        <record id="{record_id}" model="hr.leave.btl">
            <field name="employee_id" ref="{emp_ref}"/>
            <field name="leave_type">{leave_type}</field>
            <field name="date_from" eval="(DateTime.now() - timedelta(days={day_offset})).strftime('%Y-%m-%d')"/>
            <field name="date_to" eval="(DateTime.now() - timedelta(days={day_offset - num_days})).strftime('%Y-%m-%d')"/>
            <field name="number_of_days" eval="{num_days}"/>
            <field name="reason">Nghỉ phép định kỳ tháng {datetime.now().month}</field>
            <field name="state">{state}</field>
        </record>
'''
        xml_records.append(xml)
    
    return xml_records

# Generate 45 overtime records
def generate_overtime_data():
    xml_records = []
    
    for i in range(45):
        record_id = f"overtime_demo_{i+1:03d}"
        emp_num = random.randint(1, 50)
        emp_ref = f"employee_demo_{emp_num:03d}"
        
        day_offset = random.randint(0, 60)
        hours = random.choice([1.5, 2.0, 3.0, 4.0])
        ot_type = random.choice(['weekday', 'weekend', 'holiday'])
        state = random.choice(['draft', 'confirmed', 'approved', 'paid'])
        
        xml = f'''        <record id="{record_id}" model="hr.overtime">
            <field name="employee_id" ref="{emp_ref}"/>
            <field name="date" eval="(DateTime.now() - timedelta(days={day_offset})).strftime('%Y-%m-%d')"/>
            <field name="hours" eval="{hours}"/>
            <field name="overtime_type">{ot_type}</field>
            <field name="reason">Tăng ca xử lý dự án khẩn</field>
            <field name="state">{state}</field>
        </record>
'''
        xml_records.append(xml)
    
    return xml_records

# Main
if __name__ == '__main__':
    print('<?xml version="1.0" encoding="utf-8"?>')
    print('<odoo>')
    print('    <data noupdate="1">')
    print()
    print('        <!-- 60 Attendance Records -->')
    
    attendance_records = generate_attendance_data()
    for rec in attendance_records:
        print(rec)
    
    print()
    print('        <!-- 45 Leave Records -->')
    
    leave_records = generate_leave_data()
    for rec in leave_records:
        print(rec)
    
    print()
    print('        <!-- 45 Overtime Records -->')
    
    overtime_records = generate_overtime_data()
    for rec in overtime_records:
        print(rec)
    
    print('    </data>')
    print('</odoo>')
    
    print(f"\n<!-- Total: {len(attendance_records) + len(leave_records) + len(overtime_records)} records -->", file=open('/dev/stderr', 'w') if __name__ == '__main__' else None)
