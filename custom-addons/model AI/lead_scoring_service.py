# -*- coding: utf-8 -*-
"""
Lead Scoring Service - Tích hợp AI vào Odoo
============================================
Cung cấp các hàm để dự đoán điểm chất lượng và khả năng chuyển đổi của lead
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import logging

_logger = logging.getLogger(__name__)


class LeadScoringService:
    """
    Service để dự đoán chất lượng lead sử dụng AI model
    """
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super(LeadScoringService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Khởi tạo service"""
        if self._initialized:
            return
            
        self.model_dir = os.path.dirname(os.path.abspath(__file__))
        self.model = None
        self.scaler = None
        self.encoders = None
        self.feature_names = None
        self._load_model()
        self._initialized = True
    
    def _load_model(self):
        """Tải mô hình từ file"""
        try:
            model_file = os.path.join(self.model_dir, 'lead_scoring_model.pkl')
            scaler_file = os.path.join(self.model_dir, 'lead_scoring_model_scaler.pkl')
            encoders_file = os.path.join(self.model_dir, 'lead_scoring_model_encoders.pkl')
            features_file = os.path.join(self.model_dir, 'lead_scoring_model_features.pkl')
            
            if os.path.exists(model_file):
                self.model = joblib.load(model_file)
                self.scaler = joblib.load(scaler_file)
                self.encoders = joblib.load(encoders_file)
                self.feature_names = joblib.load(features_file)
                _logger.info("✓ Lead Scoring Model loaded successfully")
            else:
                _logger.warning("⚠ Lead Scoring Model file not found")
        except Exception as e:
            _logger.error(f"✗ Error loading Lead Scoring Model: {str(e)}")
    
    def is_model_loaded(self):
        """Kiểm tra xem model có được tải không"""
        return self.model is not None
    
    def predict_lead_quality(self, lead_data):
        """
        Dự đoán điểm chất lượng lead (0-100)
        
        Args:
            lead_data (dict): Dữ liệu lead
                {
                    'company_size': str,
                    'budget': int,
                    'num_calls': int,
                    'num_emails': int,
                    'num_meetings': int,
                    'days_since_interaction': int,
                    'response_rate': float,
                    'email_open_rate': float,
                    'page_views': int,
                    'lead_age_days': int,
                    'priority_score': int,
                    'quality_score': int
                }
        
        Returns:
            dict: {
                'conversion_probability': float (0-100),
                'quality_score': int (0-100),
                'will_convert': bool,
                'confidence': float (0-1)
            }
        """
        if not self.is_model_loaded():
            _logger.warning("Model not loaded, returning default scoring")
            return self._get_default_scoring(lead_data)
        
        try:
            # Chuẩn bị dữ liệu
            df = pd.DataFrame([lead_data])
            df_processed = self._prepare_features(df)
            
            # Dự đoán
            X_scaled = self.scaler.transform(df_processed[self.feature_names])
            prediction = self.model.predict(X_scaled)[0]
            probability = self.model.predict_proba(X_scaled)[0, 1]
            
            # Tính toán conversion probability (0-100)
            conversion_prob = probability * 100
            
            # Tính quality score (0-100)
            quality_score = min(100, max(0, int(
                (conversion_prob * 0.6) +  # 60% từ AI model
                (lead_data.get('quality_score', 50) * 0.4)  # 40% từ manual score
            )))
            
            # Xác định sẽ chuyển đổi hay không (>50% xác suất)
            will_convert = probability > 0.5
            
            # Confidence score
            confidence = min(probability, 1 - probability) * 2
            
            result = {
                'conversion_probability': round(conversion_prob, 2),
                'quality_score': quality_score,
                'will_convert': will_convert,
                'confidence': round(confidence, 3),
                'risk_level': self._get_risk_level(conversion_prob)
            }
            
            _logger.info(f"Lead scoring prediction: {result}")
            return result
            
        except Exception as e:
            _logger.error(f"Error in prediction: {str(e)}")
            return self._get_default_scoring(lead_data)
    
    def _prepare_features(self, df):
        """Chuẩn bị features từ raw data"""
        df_processed = df.copy()
        
        # Encode categorical
        for col in ['company_size', 'industry']:
            if col in df_processed.columns and col in self.encoders:
                try:
                    df_processed[col] = self.encoders[col].transform(df_processed[col])
                except:
                    df_processed[col] = 0
        
        # Thêm missing columns với giá trị mặc định
        for col in self.feature_names:
            if col not in df_processed.columns:
                df_processed[col] = 0
        
        # Feature engineering
        df_processed['total_interactions'] = (
            df_processed.get('num_calls', 0) + 
            df_processed.get('num_emails', 0) + 
            df_processed.get('num_meetings', 0)
        )
        
        df_processed['engagement_score'] = (
            df_processed.get('response_rate', 0) * 0.3 +
            df_processed.get('email_open_rate', 0) * 0.4 +
            (df_processed.get('page_views', 0) / 100) * 0.3
        )
        
        days_since = df_processed.get('days_since_interaction', 30)
        df_processed['recency_score'] = 1.0 / (1.0 + days_since / 30.0)
        
        lead_age = df_processed.get('lead_age_days', 30)
        df_processed['lead_maturity'] = 1.0 / (1.0 + np.exp(-((lead_age - 60) / 30.0)))
        
        return df_processed
    
    def _get_risk_level(self, conversion_prob):
        """Xác định mức độ rủi ro"""
        if conversion_prob >= 80:
            return 'very_high'  # Rất cao
        elif conversion_prob >= 60:
            return 'high'  # Cao
        elif conversion_prob >= 40:
            return 'medium'  # Trung bình
        elif conversion_prob >= 20:
            return 'low'  # Thấp
        else:
            return 'very_low'  # Rất thấp
    
    def _get_default_scoring(self, lead_data):
        """Trả về scoring mặc định khi model không available"""
        # Tính toán cơ bản dựa trên các trường có sẵn
        quality = lead_data.get('quality_score', 50)
        
        return {
            'conversion_probability': float(quality),
            'quality_score': quality,
            'will_convert': quality >= 60,
            'confidence': 0.0,
            'risk_level': self._get_risk_level(quality)
        }
    
    def batch_predict(self, leads_data):
        """
        Dự đoán hàng loạt nhiều lead
        
        Args:
            leads_data (list): Danh sách lead data
        
        Returns:
            list: Danh sách kết quả dự đoán
        """
        results = []
        for lead_data in leads_data:
            result = self.predict_lead_quality(lead_data)
            results.append(result)
        return results


# Instance duy nhất
_lead_scoring_service = None


def get_lead_scoring_service():
    """Get singleton instance of Lead Scoring Service"""
    global _lead_scoring_service
    if _lead_scoring_service is None:
        _lead_scoring_service = LeadScoringService()
    return _lead_scoring_service
