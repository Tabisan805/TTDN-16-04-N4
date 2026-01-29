# -*- coding: utf-8 -*-
{
    'name': 'BTL - Quản lý Công việc & Hoạt động',
    'version': '19.0.1.0.0',
    'category': 'BTL/Project Management',
    'summary': 'Quản lý công việc, hoạt động và theo dõi hiệu suất',
    'description': """
        Module Quản lý Công việc & Hoạt động BTL
        ==========================================
        
        Tính năng chính:
        ----------------
        * Quản lý Task và Activity
        * Tự động chuyển hóa tương tác thành công việc
        * Phân loại công việc theo phòng ban
        * Quản lý bàn giao công việc
        * Lịch sử thay đổi công việc
        * Báo cáo hiệu suất theo thời gian
        * Dashboard theo vai trò
        * Phân quyền chi tiết
        
        Phạm vi áp dụng:
        ----------------
        * Quản lý: Giao việc, theo dõi tiến độ
        * Sale: Follow-up khách hàng, báo giá
        * Marketing: Chiến dịch, nội dung
        * Kế toán: Hóa đơn, thanh toán
        * Nhân sự: Tuyển dụng, đánh giá
        * Trợ lý: Sắp xếp lịch, hỗ trợ
    """,
    'author': 'BTL Team',
    'website': 'https://www.btl.com',
    'depends': [
        'base',
        'project',
        'mail',
        'calendar',
        'hr',
        'crm',
        'sale',
    ],
    'data': [
        # Security
        'security/task_security.xml',
        'security/ir.model.access.csv',
        
        # Data
        'data/task_type_data.xml',
        'data/handover_stage_data.xml',
        'data/customers_employees_data.xml',
        'data/demo_data.xml',
        
        # Wizards
        'wizards/task_handover_wizard_views.xml',
        
        # Views
        'views/task_type_views.xml',
        'views/project_task_views.xml',
        'views/task_handover_views.xml',
        'views/task_handover_stage_views.xml',
        'views/task_performance_views.xml',
        'views/menu_views.xml',
    ],
    'demo': [
        'data/demo_data.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
