#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo Lead Data Generator for AI Model Testing
Tạo dữ liệu khách hàng mẫu để kiểm tra mô hình AI
"""

import os
import sys
import django
from datetime import datetime, timedelta
import random

# Setup Django/Odoo
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
sys.path.insert(0, '/mnt/custom-addons')

# Sample data templates
COMPANY_SIZES = ['1-10', '11-50', '51-200', '201-500', '500+']
INDUSTRIES = ['Công nghệ', 'Bán lẻ', 'Sản xuất', 'Bất động sản', 'Tài chính', 'Y tế', 'Giáo dục', 'Dịch vụ']
BUDGETS = [10000, 25000, 50000, 100000, 250000, 500000, 1000000]
PRIORITIES = ['0', '1', '2', '3']  # Low, Medium, High, Very High
STAGES = ['new', 'qualified', 'proposition', 'won', 'lost']

DEMO_LEADS = [
    # High probability leads (sẽ chuyển đổi)
    {
        'name': 'Công ty TNHH ABC Technology',
        'contact_name': 'Nguyễn Văn A',
        'email_from': 'contact@abc-tech.com',
        'phone': '0987654321',
        'company_size': '51-200',
        'industry_btl': 'Công nghệ',
        'budget': 500000,
        'quality_score': 85,
        'priority_btl': '3',
        'stage_status': 'proposition',
        'days_ago': 5,
        'interactions': 12,
        'description': 'Lead từ sự kiện tech summit, rất quan tâm đến giải pháp'
    },
    {
        'name': 'Tập đoàn XYZ Retail',
        'contact_name': 'Trần Thị B',
        'email_from': 'b.tran@xyz-retail.vn',
        'phone': '0912345678',
        'company_size': '201-500',
        'industry_btl': 'Bán lẻ',
        'budget': 1000000,
        'quality_score': 90,
        'priority_btl': '3',
        'stage_status': 'proposition',
        'days_ago': 3,
        'interactions': 15,
        'description': 'Lead tìm kiếm chủ động, đã gửi yêu cầu báo giá'
    },
    {
        'name': 'Công ty Cổ phần DEF Manufacturing',
        'contact_name': 'Lê Minh C',
        'email_from': 'c.le@def-mfg.com',
        'phone': '0923456789',
        'company_size': '11-50',
        'industry_btl': 'Sản xuất',
        'budget': 250000,
        'quality_score': 75,
        'priority_btl': '2',
        'stage_status': 'qualified',
        'days_ago': 7,
        'interactions': 8,
        'description': 'Lead từ đề xuất, đã có cuộc họp khám phá nhu cầu'
    },
    {
        'name': 'Công ty GHI Real Estate',
        'contact_name': 'Phạm Quý D',
        'email_from': 'd.pham@ghi-realestate.vn',
        'phone': '0934567890',
        'company_size': '51-200',
        'industry_btl': 'Bất động sản',
        'budget': 750000,
        'quality_score': 80,
        'priority_btl': '2',
        'stage_status': 'qualified',
        'days_ago': 10,
        'interactions': 6,
        'description': 'Lead có tiềm năng cao, chờ phê duyệt từ quản lý'
    },
    {
        'name': 'Ngân hàng JKL Finance',
        'contact_name': 'Đặng Thu E',
        'email_from': 'e.dang@jkl-finance.com',
        'phone': '0945678901',
        'company_size': '201-500',
        'industry_btl': 'Tài chính',
        'budget': 1000000,
        'quality_score': 88,
        'priority_btl': '3',
        'stage_status': 'proposition',
        'days_ago': 8,
        'interactions': 10,
        'description': 'Lead từ partner, có nhu cầu rõ ràng'
    },
    
    # Medium probability leads
    {
        'name': 'Phòng khám MNO Health',
        'contact_name': 'Võ Hoàng F',
        'email_from': 'f.vo@mno-health.vn',
        'phone': '0956789012',
        'company_size': '11-50',
        'industry_btl': 'Y tế',
        'budget': 100000,
        'quality_score': 55,
        'priority_btl': '1',
        'stage_status': 'qualified',
        'days_ago': 15,
        'interactions': 3,
        'description': 'Lead từ khảo sát, quan tâm nhưng chưa quyết định'
    },
    {
        'name': 'Trường Đại học PQR Education',
        'contact_name': 'Hoàng Yến G',
        'email_from': 'g.hoang@pqr-edu.vn',
        'phone': '0967890123',
        'company_size': '51-200',
        'industry_btl': 'Giáo dục',
        'budget': 200000,
        'quality_score': 60,
        'priority_btl': '1',
        'stage_status': 'new',
        'days_ago': 20,
        'interactions': 2,
        'description': 'Lead từ cold outreach, cần tìm hiểu thêm'
    },
    {
        'name': 'Công ty Dịch vụ STU Services',
        'contact_name': 'Trương Khánh H',
        'email_from': 'h.truong@stu-services.vn',
        'phone': '0978901234',
        'company_size': '1-10',
        'industry_btl': 'Dịch vụ',
        'budget': 50000,
        'quality_score': 50,
        'priority_btl': '0',
        'stage_status': 'new',
        'days_ago': 25,
        'interactions': 1,
        'description': 'Lead mới, chưa có tương tác'
    },
    {
        'name': 'Tập đoàn VWX Logistics',
        'contact_name': 'Cao Trọng I',
        'email_from': 'i.cao@vwx-logistics.com',
        'phone': '0989012345',
        'company_size': '201-500',
        'industry_btl': 'Dịch vụ',
        'budget': 400000,
        'quality_score': 65,
        'priority_btl': '1',
        'stage_status': 'qualified',
        'days_ago': 12,
        'interactions': 4,
        'description': 'Lead từ tham khảo, có nhu cầu nhưng đang so sánh'
    },
    
    # Low probability leads
    {
        'name': 'Startup YZA Innovations',
        'contact_name': 'Bùi Minh J',
        'email_from': 'j.bui@yza-startup.io',
        'phone': '0990123456',
        'company_size': '1-10',
        'industry_btl': 'Công nghệ',
        'budget': 25000,
        'quality_score': 30,
        'priority_btl': '0',
        'stage_status': 'new',
        'days_ago': 45,
        'interactions': 0,
        'description': 'Lead từ webinar, budget thấp'
    },
    {
        'name': 'Quán Cà phê ABC Coffee',
        'contact_name': 'Huỳnh Mai K',
        'email_from': 'k.huynh@abc-coffee.vn',
        'phone': '0901234567',
        'company_size': '1-10',
        'industry_btl': 'Bán lẻ',
        'budget': 10000,
        'quality_score': 20,
        'priority_btl': '0',
        'stage_status': 'lost',
        'days_ago': 60,
        'interactions': 0,
        'description': 'Lead không phù hợp, loại bỏ'
    },
    {
        'name': 'Công ty BCD Import Export',
        'contact_name': 'Ngô Thị L',
        'email_from': 'l.ngo@bcd-import.vn',
        'phone': '0912345670',
        'company_size': '11-50',
        'industry_btl': 'Bán lẻ',
        'budget': 30000,
        'quality_score': 35,
        'priority_btl': '0',
        'stage_status': 'new',
        'days_ago': 50,
        'interactions': 0,
        'description': 'Lead mặc định, chưa liên hệ'
    },
    {
        'name': 'Dự án Nhà ở EFG Properties',
        'contact_name': 'Lý Nhật M',
        'email_from': 'm.ly@efg-properties.vn',
        'phone': '0923456781',
        'company_size': '51-200',
        'industry_btl': 'Bất động sản',
        'budget': 100000,
        'quality_score': 40,
        'priority_btl': '0',
        'stage_status': 'lost',
        'days_ago': 90,
        'interactions': 1,
        'description': 'Lead không đáp ứng, tạm ngừng'
    },
    {
        'name': 'Công ty HIJ Consulting',
        'contact_name': 'Vũ Huy N',
        'email_from': 'n.vu@hij-consulting.vn',
        'phone': '0934567892',
        'company_size': '11-50',
        'industry_btl': 'Dịch vụ',
        'budget': 75000,
        'quality_score': 45,
        'priority_btl': '1',
        'stage_status': 'new',
        'days_ago': 35,
        'interactions': 1,
        'description': 'Lead có tiềm năng vừa phải'
    },
]


def generate_demo_leads():
    """
    Generate demo lead records for AI model testing
    Tạo dữ liệu lead mẫu để kiểm tra mô hình AI
    """
    print("=" * 80)
    print("Demo Lead Data Generator for AI Model Testing")
    print("Tạo dữ liệu khách hàng mẫu cho mô hình AI")
    print("=" * 80)
    
    # SQL INSERT statements
    sql_statements = []
    
    for i, lead_data in enumerate(DEMO_LEADS, 1):
        # Calculate dates
        create_date = datetime.now() - timedelta(days=lead_data['days_ago'])
        
        # Build INSERT statement
        sql = f"""
INSERT INTO crm_lead (
    name, 
    contact_name, 
    email_from, 
    phone, 
    company_size, 
    industry_btl, 
    budget, 
    quality_score, 
    priority_btl, 
    stage_status,
    probability,
    description,
    type,
    active,
    create_date,
    write_date,
    user_id,
    company_id
) VALUES (
    '{lead_data['name']}',
    '{lead_data['contact_name']}',
    '{lead_data['email_from']}',
    '{lead_data['phone']}',
    '{lead_data['company_size']}',
    '{lead_data['industry_btl']}',
    {lead_data['budget']},
    {lead_data['quality_score']},
    '{lead_data['priority_btl']}',
    '{lead_data['stage_status']}',
    {75 if lead_data['stage_status'] == 'proposition' else 50 if lead_data['stage_status'] == 'qualified' else 25},
    '{lead_data['description']}',
    'lead',
    true,
    '{create_date.isoformat()}',
    NOW(),
    2,
    1
);
"""
        sql_statements.append(sql)
        print(f"✓ Lead {i}: {lead_data['name']}")
    
    # Print SQL for manual execution
    print("\n" + "=" * 80)
    print("SQL Statements for Database Insertion")
    print("=" * 80)
    print("\n".join(sql_statements))
    
    return sql_statements


if __name__ == '__main__':
    generate_demo_leads()
    print("\n✓ Demo data generator completed!")
    print("\nTo insert the data into Odoo:")
    print("1. Copy the SQL statements above")
    print("2. Execute in PostgreSQL database")
    print("3. Refresh Odoo page to see new leads")
