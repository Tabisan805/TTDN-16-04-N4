# -*- coding: utf-8 -*-
{
    'name': 'BTL - Quản lý Nhân sự',
    'version': '19.0.1.0.0',
    'category': 'BTL/Human Resources',
    'summary': 'Quản lý thời gian, ngày công, thưởng phạt, lương và hiệu suất',
    'description': """
        Module Quản lý Nhân sự BTL
        ==========================
        
        Chức năng chính:
        - Quản lý hồ sơ nhân sự
        - Chấm công và theo dõi thời gian ra/vào
        - Tính toán ngày công, đi trễ, về sớm, tăng ca
        - Quản lý thưởng - phạt
        - Tính lương và thu nhập
        - Theo dõi hiệu suất làm việc
        - Liên thông với CRM & Sales
    """,
    'author': 'BTL',
    'website': 'https://www.btl.com',
    'depends': [
        'base',
        'hr',
        'hr_attendance',
        'hr_holidays',
        'project',
        'sale',
        'crm',
        'account',
        'mail',
        'calendar',
    ],
    'data': [
        # Security
        'security/hr_security.xml',
        'security/ir.model.access.csv',
        
        # Data
        'data/hr_department_data.xml',
        'data/hr_job_data.xml',
        'data/hr_sequence_data.xml',
        'data/hr_reward_punishment_type_data.xml',
        'data/hr_attendance_rule_data.xml',
        'data/hr_cron_jobs.xml',
        
        # Views - Employee
        'views/hr_employee_views.xml',
        
        # Views - Attendance
        'views/hr_attendance_views.xml',
        'views/hr_attendance_rule_views.xml',
        
        # Views - Leave
        'views/hr_leave_views.xml',
        
        # Views - Overtime
        'views/hr_overtime_views.xml',
        
        # Views - Reward & Punishment
        'views/hr_reward_punishment_type_views.xml',
        'views/hr_reward_punishment_views.xml',
        
        # Views - Payroll
        'views/hr_work_entry_views.xml',
        'views/hr_payslip_views.xml',
        
        # Views - Performance
        'views/hr_performance_views.xml',
        
        # Wizards
        'wizards/hr_payslip_generate_wizard_views.xml',
        'wizards/hr_attendance_import_wizard_views.xml',
        'wizards/hr_employee_import_wizard_views.xml',
        
        # Reports
        'reports/hr_attendance_report_views.xml',
        'reports/hr_payroll_report_views.xml',
        'reports/hr_performance_report_views.xml',
        
        # Menus
        'views/hr_menu_views.xml',
    ],
    'demo': [
        'data/demo_data_employees.xml',
        'data/demo_data_attendance_leave.xml',
        'data/demo_data_weekly.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
