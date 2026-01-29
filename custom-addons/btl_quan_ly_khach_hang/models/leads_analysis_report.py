# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta

class LeadsAnalysisReport(models.Model):
    _name = 'leads.analysis.report'
    _description = 'Báo cáo Phân tích Khách hàng Tiềm năng với AI Predictive'
    _auto = False
    _rec_name = 'lead_id'

    # Lead Information
    lead_id = fields.Many2one('crm.lead', 'Khách hàng Tiềm năng', readonly=True)
    lead_name = fields.Char('Tên Khách hàng', readonly=True)
    contact_name = fields.Char('Người liên hệ', readonly=True)
    email = fields.Char('Email', readonly=True)
    phone = fields.Char('Điện thoại', readonly=True)
    
    # Company Info
    company_id = fields.Many2one('res.company', 'Công ty', readonly=True)
    
    # Financial Data
    expected_revenue = fields.Float('Budget Dự kiến (VNĐ)', readonly=True)
    
    # AI Predictive Scoring
    ai_score = fields.Integer('AI Predictive Score (%)', readonly=True)
    ai_classification = fields.Selection([
        ('hot', '🔴 Hot - Sắp ký (85-100%)'),
        ('warm', '🟡 Warm - Tiềm năng cao (60-84%)'),
        ('cold', '🔵 Cold - Tiềm năng thấp (<60%)'),
    ], 'Phân loại AI', readonly=True)
    
    # Interaction History
    total_interactions = fields.Integer('Tổng tương tác', readonly=True)
    successful_interactions = fields.Integer('Tương tác thành công', readonly=True)
    interaction_success_rate = fields.Float('Tỷ lệ thành công (%)', readonly=True)
    
    # Interaction Types
    calls_count = fields.Integer('Cuộc gọi', readonly=True)
    emails_count = fields.Integer('Email', readonly=True)
    meetings_count = fields.Integer('Cuộc họp', readonly=True)
    quotes_sent = fields.Integer('Báo giá gửi', readonly=True)
    demos_count = fields.Integer('Demo', readonly=True)
    
    # Timeline
    last_interaction_date = fields.Date('Lần tương tác cuối', readonly=True)
    days_since_last_interaction = fields.Integer('Ngày không tương tác', readonly=True)
    
    # Status
    stage_id = fields.Many2one('crm.stage', 'Giai đoạn', readonly=True)
    
    # Expected Conversion Value
    expected_conversion_value = fields.Float('Giá trị dự kiến chuyển đổi (VNĐ)', readonly=True)
    
    # Quotations
    quotation_count = fields.Integer('Số báo giá', readonly=True)
    quotation_total = fields.Float('Tổng giá trị báo giá (VNĐ)', readonly=True)

    def init(self):
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW leads_analysis_report AS (
                SELECT
                    cl.id,
                    cl.id as lead_id,
                    cl.name as lead_name,
                    cl.contact_name,
                    cl.email_from as email,
                    cl.phone,
                    cl.company_id,
                    cl.expected_revenue,
                    COALESCE(cl.ai_score, 0) as ai_score,
                    CASE
                        WHEN COALESCE(cl.ai_score, 0) >= 85 THEN 'hot'
                        WHEN COALESCE(cl.ai_score, 0) >= 60 THEN 'warm'
                        ELSE 'cold'
                    END as ai_classification,
                    COALESCE(interaction_stats.total, 0) as total_interactions,
                    COALESCE(interaction_stats.successful, 0) as successful_interactions,
                    CASE
                        WHEN COALESCE(interaction_stats.total, 0) > 0
                        THEN ROUND((COALESCE(interaction_stats.successful, 0)::numeric / COALESCE(interaction_stats.total, 0)) * 100)
                        ELSE 0
                    END as interaction_success_rate,
                    COALESCE(interaction_stats.calls, 0) as calls_count,
                    COALESCE(interaction_stats.emails, 0) as emails_count,
                    COALESCE(interaction_stats.meetings, 0) as meetings_count,
                    COALESCE(interaction_stats.quotes, 0) as quotes_sent,
                    COALESCE(interaction_stats.demos, 0) as demos_count,
                    interaction_stats.last_date as last_interaction_date,
                    CASE
                        WHEN interaction_stats.last_date IS NULL THEN NULL
                        ELSE EXTRACT(DAY FROM now()::timestamp - interaction_stats.last_date::timestamp)::integer
                    END as days_since_last_interaction,
                    cl.stage_id,
                    ROUND(cl.expected_revenue * (COALESCE(cl.ai_score, 0)::numeric / 100)) as expected_conversion_value,
                    COALESCE(quotation_stats.count, 0) as quotation_count,
                    COALESCE(quotation_stats.total, 0) as quotation_total
                FROM
                    crm_lead cl
                LEFT JOIN (
                    SELECT
                        lead_id,
                        COUNT(*) as total,
                        SUM(CASE WHEN outcome = 'successful' THEN 1 ELSE 0 END) as successful,
                        SUM(CASE WHEN interaction_type_id = 1 THEN 1 ELSE 0 END) as calls,
                        SUM(CASE WHEN interaction_type_id = 3 THEN 1 ELSE 0 END) as emails,
                        SUM(CASE WHEN interaction_type_id = 2 THEN 1 ELSE 0 END) as meetings,
                        SUM(CASE WHEN interaction_type_id = 4 THEN 1 ELSE 0 END) as quotes,
                        SUM(CASE WHEN interaction_type_id = 6 THEN 1 ELSE 0 END) as demos,
                        MAX(date) as last_date
                    FROM
                        crm_interaction
                    GROUP BY
                        lead_id
                ) interaction_stats ON cl.id = interaction_stats.lead_id
                LEFT JOIN (
                    SELECT
                        opportunity_id,
                        COUNT(*) as count,
                        SUM(amount_total) as total
                    FROM
                        sale_order
                    WHERE
                        state IN ('draft', 'sent', 'sale')
                    GROUP BY
                        opportunity_id
                ) quotation_stats ON cl.id = quotation_stats.opportunity_id
                WHERE
                    cl.type = 'lead'
            );
        """)
