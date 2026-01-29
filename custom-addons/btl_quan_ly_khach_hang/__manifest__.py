# -*- coding: utf-8 -*-
{
    'name': 'BTL - Quản lý Khách hàng',
    'version': '19.0.1.0.0',
    'category': 'BTL/Customer Management',
    'summary': 'Quản lý khách hàng tiềm năng, chính thức và lịch sử tương tác',
    'description': """
        Module Quản lý Khách hàng BTL
        ==============================
        
        Chức năng chính:
        - Quản lý khách hàng tiềm năng (Leads)
        - Quản lý khách hàng chính thức (Customers)
        - Phân loại nguồn khách hàng
        - Theo dõi lịch sử tương tác đầy đủ
        - Quản lý cuộc gọi, email, báo giá
        - Lịch hẹn và ghi chú làm việc
        - Lịch sử mua hàng và sản phẩm đã mua
        - Báo cáo và phân tích khách hàng
    """,
    'author': 'BTL',
    'website': 'https://www.btl.com',
    'depends': [
        'base',
        'crm',
        'sale',
        'sale_management',
        'contacts',
        'mail',
        'calendar',
        'account',
        'web',
        'hr',
        'project',
    ],
    'data': [
        # Security
        'security/crm_security.xml',
        'security/ir.model.access.csv',
        
        # Data
        'data/crm_source_data.xml',
        'data/crm_interaction_type_data.xml',
        'data/crm_cron_jobs.xml',
        'data/crm_lead_sample_with_details.xml',
        
        # Views - Customer Source
        'views/crm_source_views.xml',
        
        # Views - Lead (Khách hàng tiềm năng)
        'views/crm_lead_views.xml',
        
        # Views - Partner (Khách hàng chính thức)
        'views/res_partner_views.xml',
        
        # Views - Interaction
        'views/crm_interaction_type_views.xml',
        'views/crm_interaction_views.xml',
        
        # Views - Sale Order
        'views/sale_order_views.xml',
        
        # Reports
        'reports/crm_customer_report_views.xml',
        'reports/crm_interaction_report_views.xml',
        # Leads Analysis Report - DISABLED TEMPORARILY
        # 'reports/report_leads_analysis_comprehensive.xml',
        
        # Leads Analysis Views
        'views/leads_analysis_menu_final.xml',
        
        # Menus
        'views/crm_menu_views.xml',
        
        # Wizards
        'wizards/module_upgrade_wizard_views.xml',
    ],
    'demo': [
        'data/demo_data.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
