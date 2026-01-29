# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = 'crm.lead'
    
    # Nguồn khách hàng BTL
    source_btl_id = fields.Many2one('crm.source.btl', string='Nguồn khách hàng', tracking=True)
    
    # Nhân viên phụ trách
    employee_id = fields.Many2one('hr.employee', string='Nhân viên phụ trách',
                                  compute='_compute_employee_id', store=True,
                                  help='Nhân viên phụ trách cơ hội này')
    employee_name = fields.Char(related='employee_id.name', string='Tên nhân viên')
    employee_department = fields.Char(related='employee_id.department_id.name', string='Phòng ban')
    
    # Thông tin bổ sung
    company_size = fields.Selection([
        ('1-10', '1-10 nhân viên'),
        ('11-50', '11-50 nhân viên'),
        ('51-200', '51-200 nhân viên'),
        ('201-500', '201-500 nhân viên'),
        ('500+', 'Trên 500 nhân viên'),
    ], string='Quy mô công ty')
    
    industry_btl = fields.Char(string='Ngành nghề')
    tax_code = fields.Char(string='Mã số thuế')
    
    # Sản phẩm quan tâm
    interested_product_ids = fields.Many2many('product.product', string='Sản phẩm quan tâm')
    company_currency = fields.Many2one('res.currency', string='Tiền tệ', 
                                       related='company_id.currency_id', readonly=True)
    budget = fields.Monetary(string='Ngân sách dự kiến', currency_field='company_currency')
    
    # Lịch sử tương tác
    interaction_ids = fields.One2many('crm.interaction', 'lead_id', string='Lịch sử tương tác')
    interaction_count = fields.Integer(string='Số lần tương tác', compute='_compute_interaction_count')
    last_interaction_date = fields.Datetime(string='Tương tác gần nhất', compute='_compute_last_interaction')
    
    # Thống kê
    total_calls = fields.Integer(string='Số cuộc gọi', compute='_compute_interaction_statistics')
    total_meetings = fields.Integer(string='Số cuộc họp', compute='_compute_interaction_statistics')
    total_emails = fields.Integer(string='Số email', compute='_compute_interaction_statistics')
    
    # Phân loại
    priority_btl = fields.Selection([
        ('0', 'Thấp'),
        ('1', 'Trung bình'),
        ('2', 'Cao'),
        ('3', 'Rất cao'),
    ], string='Độ ưu tiên', default='1')
    
    quality_score = fields.Integer(string='Điểm chất lượng', help='Đánh giá chất lượng lead từ 0-100')
    
    # Xác suất thành công
    probability = fields.Float(string='Xác suất (%)', default=10.0, 
                               help='Xác suất chuyển đổi thành khách hàng (0-100%)')
    
    # Workflow stages
    stage_status = fields.Selection([
        ('new', 'Mới'),
        ('qualified', 'Đã liên hệ'),
        ('proposition', 'Đang đàm phán'),
        ('won', 'Đã thắng'),
        ('lost', 'Đã thua'),
    ], string='Giai đoạn', default='new', tracking=True)
    
    # AI Predictive Lead Scoring Fields
    ai_score = fields.Float(
        string='Điểm dự đoán AI (%)', 
        compute='_compute_ai_score',
        store=True,
        help='Điểm dự đoán khả năng chuyển đổi từ AI model (0-100%)'
    )
    
    ai_will_convert = fields.Boolean(
        string='Dự đoán chuyển đổi',
        compute='_compute_ai_score',
        store=True,
        help='Dự đoán lead sẽ chuyển đổi thành khách hàng hay không'
    )
    
    ai_confidence = fields.Float(
        string='Độ tin cậy (%)',
        compute='_compute_ai_score',
        store=True,
        default=30.0,
        help='Mức độ tin cậy của dự đoán (30-90%)'
    )
    
    ai_risk_level = fields.Selection([
        ('very_high', 'Rất cao'),
        ('high', 'Cao'),
        ('medium', 'Trung bình'),
        ('low', 'Thấp'),
        ('very_low', 'Rất thấp'),
    ], string='Mức rủi ro', compute='_compute_ai_score', store=True,
        help='Mức rủi ro của lead')
    
    ai_last_update = fields.Datetime(
        string='Cập nhật cuối',
        compute='_compute_ai_score',
        store=True,
        help='Lần cập nhật dự đoán cuối cùng'
    )
    
    # AI Confidence & Risk Factors
    ai_confidence_factors = fields.Char(
        string='Yếu tố độ tin cậy',
        compute='_compute_ai_score',
        store=True,
        help='Chi tiết các yếu tố ảnh hưởng đến độ tin cậy'
    )
    
    ai_risk_factors = fields.Text(
        string='Yếu tố rủi ro',
        compute='_compute_ai_score',
        store=True,
        help='Chi tiết các yếu tố rủi ro của lead'
    )
    
    ai_confidence_reasoning = fields.Text(
        string='Giải thích độ tin cậy',
        compute='_compute_ai_score',
        store=True,
        help='Giải thích chi tiết tính toán độ tin cậy'
    )
    
    @api.depends('user_id')
    def _compute_employee_id(self):
        """Tìm nhân viên dựa trên user_id"""
        for lead in self:
            if lead.user_id:
                employee = self.env['hr.employee'].search([
                    ('user_id', '=', lead.user_id.id)
                ], limit=1)
                lead.employee_id = employee.id if employee else False
            else:
                lead.employee_id = False
    
    @api.depends('interaction_ids')
    def _compute_interaction_count(self):
        for lead in self:
            lead.interaction_count = len(lead.interaction_ids)
    
    @api.depends('interaction_ids.date')
    def _compute_last_interaction(self):
        for lead in self:
            if lead.interaction_ids:
                lead.last_interaction_date = max(lead.interaction_ids.mapped('date'))
            else:
                lead.last_interaction_date = False
    
    @api.depends('interaction_ids.interaction_type_id')
    def _compute_interaction_statistics(self):
        for lead in self:
            interactions = lead.interaction_ids.filtered(lambda i: i.state == 'done')
            
            # Đếm theo loại (giả sử có các loại với code cụ thể)
            lead.total_calls = len(interactions.filtered(
                lambda i: 'call' in i.interaction_type_id.code.lower()
            ))
            lead.total_meetings = len(interactions.filtered(
                lambda i: 'meeting' in i.interaction_type_id.code.lower()
            ))
            lead.total_emails = len(interactions.filtered(
                lambda i: 'email' in i.interaction_type_id.code.lower()
            ))
    
    def action_view_interactions(self):
        """Xem tất cả tương tác"""
        return {
            'name': _('Lịch sử tương tác'),
            'type': 'ir.actions.act_window',
            'res_model': 'crm.interaction',
            'view_mode': 'tree,form',
            'domain': [('lead_id', '=', self.id)],
            'context': {'default_lead_id': self.id, 'default_partner_id': self.partner_id.id},
        }
    
    def action_create_interaction(self):
        """Tạo tương tác mới"""
        return {
            'name': _('Tạo tương tác'),
            'type': 'ir.actions.act_window',
            'res_model': 'crm.interaction',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_lead_id': self.id,
                'default_partner_id': self.partner_id.id,
                'default_title': f'Tương tác với {self.name}',
            },
        }
    
    def action_convert_to_customer(self):
        """Chuyển đổi Lead thành Khách hàng"""
        self.ensure_one()
        
        # Tạo hoặc cập nhật partner
        if not self.partner_id:
            partner_vals = {
                'name': self.contact_name or self.name,
                'phone': self.phone,
                'mobile': self.mobile if hasattr(self, 'mobile') else False,
                'email': self.email_from,
                'street': self.street,
                'street2': self.street2,
                'city': self.city,
                'state_id': self.state_id.id,
                'zip': self.zip,
                'country_id': self.country_id.id,
                'website': self.website,
                'customer_type_btl': 'regular',
                'source_btl_id': self.source_btl_id.id,
                'company_size': self.company_size,
                'industry_btl': self.industry_btl,
                'tax_code': self.tax_code,
                'user_id': self.user_id.id,
            }
            partner = self.env['res.partner'].create(partner_vals)
            self.partner_id = partner.id
        else:
            # Cập nhật thông tin customer
            self.partner_id.write({'customer_type_btl': 'regular'})
        
        # Chuyển lead sang opportunity và won
        if self.type != 'opportunity':
            self.write({'type': 'opportunity'})
        
        self.stage_status = 'won'
        
        # Tạo thông báo
        message = f"Lead đã được chuyển đổi thành khách hàng: {self.partner_id.name}"
        self.message_post(body=message, subject='Chuyển đổi thành công')
        
        # Mở form khách hàng
        return {
            'name': _('Khách hàng'),
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'res_id': self.partner_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_update_probability(self):
        """Cập nhật xác suất dựa trên giai đoạn"""
        for lead in self:
            if lead.stage_status == 'new':
                lead.probability = 10.0
            elif lead.stage_status == 'qualified':
                lead.probability = 30.0
            elif lead.stage_status == 'proposition':
                lead.probability = 60.0
            elif lead.stage_status == 'won':
                lead.probability = 100.0
            elif lead.stage_status == 'lost':
                lead.probability = 0.0
    
    @api.onchange('stage_status')
    def _onchange_stage_status(self):
        """Tự động cập nhật xác suất khi thay đổi giai đoạn"""
        self.action_update_probability()
    
    @api.model
    def _cron_update_lead_probability(self):
        """Cron job: Cập nhật xác suất lead dựa trên thời gian và hoạt động"""
        # Cập nhật xác suất cho tất cả lead đang active
        leads = self.search([
            ('type', '=', 'lead'),
            ('active', '=', True),
            ('stage_status', 'not in', ['won', 'lost'])
        ])
        
        for lead in leads:
            lead.action_update_probability()
    
    # ===================== AI PREDICTIVE SCORING METHODS =====================
    
    def _get_lead_scoring_data(self):
        """
        Chuẩn bị dữ liệu lead để dự đoán với AI
        
        Returns:
            dict: Dữ liệu lead định dạng cho AI model
        """
        self.ensure_one()
        
        # Tính toán thống kê tương tác
        interactions = self.interaction_ids.filtered(lambda i: i.state == 'done')
        
        # Tính days since last interaction
        if interactions:
            last_date = max(interactions.mapped('date'))
            days_since = (datetime.now() - last_date).days if last_date else 90
        else:
            days_since = 90
        
        # Tính response rate
        if interactions:
            responded = len(interactions.filtered(lambda i: i.response_status == 'responded'))
            response_rate = responded / len(interactions) if interactions else 0
        else:
            response_rate = 0
        
        # Tính days since lead creation
        lead_age = (datetime.now().date() - self.create_date.date()).days if self.create_date else 0
        
        # Chuẩn bị dữ liệu
        lead_data = {
            'company_size': self.company_size or '1-10',
            'budget': int(self.budget) if self.budget else 0,
            'num_calls': self.total_calls,
            'num_emails': self.total_emails,
            'num_meetings': self.total_meetings,
            'days_since_interaction': min(days_since, 90),
            'response_rate': min(response_rate, 1.0),
            'email_open_rate': 0.5,  # Giá trị mặc định (có thể integrate với email system)
            'page_views': 10,  # Giá trị mặc định (có thể integrate với website tracking)
            'lead_age_days': min(lead_age, 365),
            'priority_score': int(self.priority_btl or 1),
            'quality_score': self.quality_score or 50,
        }
        
        return lead_data
    
    @api.depends('interaction_ids', 'interaction_ids.interaction_type_id', 'interaction_ids.state', 'quality_score', 'budget', 'company_size')
    def _compute_ai_score(self):
        """
        Tính toán AI score cho lead từ lịch sử tương tác
        
        📊 CÔNG THỨC TÍNH ĐIỂM DỰ ĐOÁN AI (0-100):
        ============================================
        1. ĐIỂM CƠ SỞ: 10 điểm
        
        2. ĐIỂM TỪ LỊCH SỬ TƯƠNG TÁC:
           - Cuộc gọi (call): +3 điểm/lần
           - Email: +2 điểm/lần
           - Cuộc họp (meeting): +5 điểm/lần
           - Báo giá (quote): +20 điểm/lần
           - Demo: +7 điểm/lần
           - Thành công (success): +5 điểm bổ sung
        
        3. THƯỞNG CHẤT LƯỢNG LEAD:
           - Từ quality_score (0-100): +30% max
           - Công thức: (quality_score * 0.3) max 30 điểm
        
        4. THƯỞNG NGÂN SÁCH:
           - ≥ 1 tỷ VND: +15 điểm
           - ≥ 500 triệu: +10 điểm
           - ≥ 100 triệu: +5 điểm
        
        5. THƯỞNG QUY MÔ CÔNG TY:
           - 500+ / 201-500 nhân viên: +10 điểm
           - 51-200 / 11-50 nhân viên: +5 điểm
        
        6. CAP: Tối đa 100 điểm
        
        📈 CÔNG THỨC TÍNH ĐỘ TIN CẬY (Confidence):
        ==========================================
        confidence = 30% + (AI_Score / 100) * 60%
        Min: 30%, Max: 90%
        
        Giải thích:
        - Base 30%: Độ tin cậy tối thiểu (có dữ liệu tương tác)
        - +Score%: Tăng thêm dựa trên điểm số (60% max)
        
        ⚠️ CÔNG THỨC TÍNH MỨC RỦI RO:
        ============================
        - Rất Cao (Very High): Score ≥ 80 (Rủi ro thấp, khả năng cao)
        - Cao (High): Score 60-80 (Tốt, nên follow-up)
        - Trung Bình (Medium): Score 40-60 (Cần xem xét)
        - Thấp (Low): Score 20-40 (Rủi ro cao)
        - Rất Thấp (Very Low): Score < 20 (Rủi ro rất cao)
        """
        for lead in self:
            # Tính điểm cơ sở
            score = 10.0
            detail_breakdown = []
            detail_breakdown.append("📊 Chi tiết tính toán AI Score:\n")
            detail_breakdown.append(f"1. Điểm cơ sở: {score}")
            
            # Lấy lịch sử tương tác
            interactions = lead.interaction_ids
            interaction_score = 0
            
            if interactions:
                for interaction in interactions:
                    interaction_type = interaction.interaction_type_id.name.lower() if interaction.interaction_type_id else ''
                    
                    # Cộng điểm theo loại tương tác
                    if 'call' in interaction_type or 'cuộc gọi' in interaction_type:
                        interaction_score += 3
                    elif 'email' in interaction_type:
                        interaction_score += 2
                    elif 'meeting' in interaction_type or 'họp' in interaction_type or 'cuộc họp' in interaction_type:
                        interaction_score += 5
                    elif 'quote' in interaction_type or 'báo giá' in interaction_type:
                        interaction_score += 20
                    elif 'demo' in interaction_type:
                        interaction_score += 7
                    
                    # Cộng thêm điểm nếu tương tác thành công
                    if interaction.outcome == 'successful':
                        interaction_score += 5
                
                score += interaction_score
                detail_breakdown.append(f"2. Điểm từ tương tác: +{interaction_score}")
            else:
                detail_breakdown.append("2. Điểm từ tương tác: 0 (chưa có tương tác)")
            
            # Cộng điểm từ quality_score
            quality_bonus = 0
            if lead.quality_score:
                quality_bonus = min(lead.quality_score * 0.3, 30)
                score += quality_bonus
                detail_breakdown.append(f"3. Thưởng chất lượng: +{quality_bonus:.1f} (từ quality score {lead.quality_score}/100)")
            else:
                detail_breakdown.append("3. Thưởng chất lượng: 0")
            
            # Cộng điểm từ ngân sách
            budget_bonus = 0
            if lead.budget and lead.budget >= 1000000000:
                budget_bonus = 15
            elif lead.budget and lead.budget >= 500000000:
                budget_bonus = 10
            elif lead.budget and lead.budget >= 100000000:
                budget_bonus = 5
            
            if budget_bonus > 0:
                score += budget_bonus
                detail_breakdown.append(f"4. Thưởng ngân sách: +{budget_bonus} (ngân sách {lead.budget:,.0f} VND)")
            else:
                detail_breakdown.append("4. Thưởng ngân sách: 0")
            
            # Cộng điểm từ công ty lớn
            company_bonus = 0
            if lead.company_size in ['500+', '201-500']:
                company_bonus = 10
            elif lead.company_size in ['51-200', '11-50']:
                company_bonus = 5
            
            if company_bonus > 0:
                score += company_bonus
                detail_breakdown.append(f"5. Thưởng quy mô: +{company_bonus} (quy mô {lead.company_size})")
            else:
                detail_breakdown.append("5. Thưởng quy mô: 0")
            
            # Limit score to max 100
            score = min(score, 100)
            detail_breakdown.append(f"\n✅ ĐIỂM AI CUỐI CÙNG: {score:.1f}/100")
            
            # Calculate Confidence with detailed explanation
            confidence_base = 30.0
            confidence_from_score = (score / 100.0) * 60.0
            confidence = confidence_base + confidence_from_score
            confidence = min(confidence, 90.0)  # Max 90%
            
            confidence_detail = []
            confidence_detail.append("📈 Chi tiết tính Độ Tin Cậy:\n")
            confidence_detail.append(f"Công thức: 30% + (AI_Score/100) × 60%")
            confidence_detail.append(f"Confidence = 30% + ({score:.1f}/100) × 60%")
            confidence_detail.append(f"Confidence = 30% + {confidence_from_score:.1f}%")
            confidence_detail.append(f"✅ ĐỘ TIN CẬY CUỐI CÙNG: {confidence:.1f}%")
            
            # Determine risk level and factors
            if score >= 80:
                risk_level = 'very_high'
                risk_emoji = '🟢'
                risk_meaning = 'Rất cao - Lead rất tiềm năng'
            elif score >= 60:
                risk_level = 'high'
                risk_emoji = '🟢'
                risk_meaning = 'Cao - Lead tiềm năng'
            elif score >= 40:
                risk_level = 'medium'
                risk_emoji = '🟡'
                risk_meaning = 'Trung bình - Cần follow-up'
            elif score >= 20:
                risk_level = 'low'
                risk_emoji = '🔴'
                risk_meaning = 'Thấp - Rủi ro cao'
            else:
                risk_level = 'very_low'
                risk_emoji = '🔴'
                risk_meaning = 'Rất thấp - Rủi ro rất cao'
            
            # Risk factors analysis
            risk_factors_list = []
            if not interactions:
                risk_factors_list.append("⚠️ Chưa có lịch sử tương tác")
            if not lead.quality_score or lead.quality_score < 50:
                risk_factors_list.append("⚠️ Điểm chất lượng thấp")
            if not lead.budget or lead.budget < 100000000:
                risk_factors_list.append("⚠️ Ngân sách không rõ hoặc thấp")
            if not lead.company_size or lead.company_size in ['1-10']:
                risk_factors_list.append("⚠️ Quy mô công ty nhỏ")
            if score < 40:
                risk_factors_list.append("⚠️ Điểm AI thấp - khả năng chuyển đổi không cao")
            
            if not risk_factors_list:
                risk_factors_text = "✅ Không phát hiện yếu tố rủi ro đáng lo ngại"
            else:
                risk_factors_text = "\n".join(risk_factors_list)
            
            # Confidence factors
            confidence_factors_list = []
            if interaction_score >= 20:
                confidence_factors_list.append("✅ Lịch sử tương tác tích cực")
            if lead.quality_score and lead.quality_score >= 70:
                confidence_factors_list.append("✅ Chất lượng lead cao")
            if lead.budget and lead.budget >= 1000000000:
                confidence_factors_list.append("✅ Ngân sách lớn")
            if lead.company_size in ['500+', '201-500']:
                confidence_factors_list.append("✅ Công ty lớn")
            if confidence >= 70:
                confidence_factors_list.append("✅ Độ tin cậy cao")
            
            if confidence_factors_list:
                confidence_factors_text = " | ".join(confidence_factors_list)
            else:
                confidence_factors_text = "Cần thêm dữ liệu"
            
            # Set all fields
            lead.ai_score = score
            lead.ai_will_convert = score >= 60
            lead.ai_confidence = confidence
            lead.ai_risk_level = risk_level
            lead.ai_last_update = datetime.now()
            lead.ai_confidence_factors = confidence_factors_text
            lead.ai_risk_factors = risk_factors_text
            lead.ai_confidence_reasoning = "\n".join(confidence_detail)
            
            _logger.info(f"Lead {lead.id}: AI Score={score:.1f}%, Confidence={confidence:.1f}%, Risk={risk_level}")
    
    
    def _get_risk_level_from_score(self, score):
        """Convert numeric score to risk level"""
        if score >= 80:
            return 'very_high'
        elif score >= 60:
            return 'high'
        elif score >= 40:
            return 'medium'
        elif score >= 20:
            return 'low'
        else:
            return 'very_low'
    
    def action_refresh_ai_score(self):
        """
        Action: Cập nhật lại AI score cho lead
        """
        for lead in self:
            lead._compute_ai_score()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Thành công',
                'message': 'Đã cập nhật AI score',
                'type': 'success',
                'sticky': False,
            }
        }
    
    @api.model
    def _cron_refresh_ai_scores(self):
        """
        Cron job: Cập nhật lại AI scores cho tất cả active leads
        """
        leads = self.search([
            ('type', '=', 'lead'),
            ('active', '=', True),
            ('stage_status', 'not in', ['won', 'lost'])
        ])
        
        _logger.info(f"Starting AI score refresh for {len(leads)} leads")
        
        for lead in leads:
            try:
                lead._compute_ai_score()
            except Exception as e:
                _logger.error(f"Error updating AI score for lead {lead.id}: {str(e)}")
        
        _logger.info("AI score refresh completed")
