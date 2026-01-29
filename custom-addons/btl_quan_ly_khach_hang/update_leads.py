#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script cập nhật thông tin chi tiết cho leads
Chạy: python3 update_leads.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

# Thêm đường dẫn server vào sys.path
sys.path.insert(0, r'c:\Program Files\Odoo 19.0.20251222\server')

# Dữ liệu chi tiết cho từng lead
LEAD_DATA = [
    {'name': 'Cung cấp thiết bị - 66', 'company_size': '201-500', 'industry': 'Manufacturing and Industrial', 'tax_code': '0101234567', 'budget': 500000000, 'quality_score': 75},
    {'name': 'Tư vấn giải pháp - 92', 'company_size': '51-200', 'industry': 'Consulting and Services', 'tax_code': '0102345678', 'budget': 250000000, 'quality_score': 60},
    {'name': 'Giải pháp phần mềm - 36', 'company_size': '11-50', 'industry': 'Information Technology', 'tax_code': '0103456789', 'budget': 150000000, 'quality_score': 85},
    {'name': 'Dịch vụ hỗ trợ kỹ thuật - 12', 'company_size': '500+', 'industry': 'Trading and Retail', 'tax_code': '0104567890', 'budget': 1000000000, 'quality_score': 90},
    {'name': 'Đầu tư dự án - 59', 'company_size': '201-500', 'industry': 'Construction and Real Estate', 'tax_code': '0105678901', 'budget': 800000000, 'quality_score': 70},
    {'name': 'Bồi dưỡng lực lượng - 82', 'company_size': '51-200', 'industry': 'Education and Training', 'tax_code': '0106789012', 'budget': 200000000, 'quality_score': 55},
    {'name': 'Nâng cao kinh doanh - 29', 'company_size': '1-10', 'industry': 'Hotel and Tourism', 'tax_code': '0107890123', 'budget': 100000000, 'quality_score': 40},
    {'name': 'Tư vấn đầu tư - 19', 'company_size': '500+', 'industry': 'Banking and Finance', 'tax_code': '0108901234', 'budget': 2000000000, 'quality_score': 95},
    {'name': 'Giải pháp quản lý - 44', 'company_size': '201-500', 'industry': 'Transportation and Logistics', 'tax_code': '0109012345', 'budget': 600000000, 'quality_score': 80},
    {'name': 'Hợp tác kinh doanh - 75', 'company_size': '51-200', 'industry': 'Agriculture and Food', 'tax_code': '0110123456', 'budget': 300000000, 'quality_score': 65},
]

print("Để cập nhật dữ liệu leads, vui lòng:")
print("1. Truy cập Odoo tại http://localhost:8069")
print("2. Đăng nhập vào hệ thống")
print("3. Vào CRM > Leads")
print("4. Cập nhật thông tin sau cho mỗi lead:")
print("   - Quy mô công ty (Công ty > 1-10 / 11-50 / 51-200 / 201-500 / 500+)")
print("   - Ngành nghề (ví dụ: Manufacturing and Industrial)")
print("   - Mã số thuế (Tax Code)")
print("   - Ngân sách dự kiến (Budget)")
print("   - Điểm chất lượng (Quality Score) từ 0-100")
print("   - Độ ưu tiên (Priority)")
print("\nHoặc sử dụng câu lệnh Python trong Odoo shell:")
print("./odoo-bin shell -d odoo19")
print(">>> env['crm.lead'].search([]).update({'company_size': '201-500', ...})")
