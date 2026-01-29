# -*- coding: utf-8 -*-
"""
Predictive Lead Scoring Model Trainer
======================================
Huấn luyện mô hình AI để dự đoán chất lượng và khả năng chuyển đổi của khách hàng tiềm năng.
"""

import os
import pickle
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, roc_auc_score
import joblib
import warnings
warnings.filterwarnings('ignore')


class PredictiveLeadScoringTrainer:
    """
    Huấn luyện mô hình Predictive Lead Scoring
    Dự đoán khả năng một lead sẽ chuyển đổi thành khách hàng
    """
    
    def __init__(self, model_path=None):
        """
        Khởi tạo trainer
        
        Args:
            model_path (str): Đường dẫn lưu model
        """
        self.model_path = model_path or os.path.dirname(__file__)
        self.model = None
        self.scaler = None
        self.encoders = {}
        self.feature_names = []
        
    def generate_sample_data(self, n_samples=500):
        """
        Tạo dữ liệu mẫu để huấn luyện mô hình
        (Trong thực tế, dữ liệu sẽ được lấy từ Odoo database)
        
        Args:
            n_samples (int): Số lượng mẫu dữ liệu
            
        Returns:
            DataFrame: Dữ liệu mẫu
        """
        np.random.seed(42)
        
        data = {
            # Thông tin cơ bản
            'company_size': np.random.choice(['1-10', '11-50', '51-200', '201-500', '500+'], n_samples),
            'industry': np.random.choice(['Technology', 'Finance', 'Retail', 'Manufacturing', 'Healthcare', 'Education'], n_samples),
            'budget': np.random.randint(10000, 1000000, n_samples),
            
            # Tương tác
            'num_calls': np.random.randint(0, 20, n_samples),
            'num_emails': np.random.randint(0, 30, n_samples),
            'num_meetings': np.random.randint(0, 15, n_samples),
            'days_since_interaction': np.random.randint(0, 90, n_samples),
            
            # Engagement
            'response_rate': np.random.uniform(0, 1, n_samples),
            'email_open_rate': np.random.uniform(0, 1, n_samples),
            'page_views': np.random.randint(0, 100, n_samples),
            
            # Lead properties
            'lead_age_days': np.random.randint(1, 365, n_samples),
            'priority_score': np.random.choice([0, 1, 2, 3], n_samples),
            'quality_score': np.random.randint(0, 100, n_samples),
            
            # Conversion indicator
            'converted': np.random.choice([0, 1], n_samples, p=[0.7, 0.3])
        }
        
        df = pd.DataFrame(data)
        
        # Thêm logic để tạo tương quan
        # Các lead có ngân sách cao, nhiều tương tác, và email open rate cao có khả năng chuyển đổi cao hơn
        high_quality_mask = (
            (df['budget'] > 500000) & 
            (df['num_meetings'] > 5) & 
            (df['email_open_rate'] > 0.5)
        )
        df.loc[high_quality_mask, 'converted'] = np.where(
            np.random.random(high_quality_mask.sum()) > 0.3, 1, 0
        )
        
        low_quality_mask = (
            (df['budget'] < 50000) & 
            (df['num_meetings'] < 2) & 
            (df['response_rate'] < 0.2)
        )
        df.loc[low_quality_mask, 'converted'] = np.where(
            np.random.random(low_quality_mask.sum()) > 0.8, 1, 0
        )
        
        return df
    
    def prepare_features(self, df):
        """
        Chuẩn bị features từ raw data
        
        Args:
            df (DataFrame): Raw data
            
        Returns:
            DataFrame: Processed features
        """
        df_processed = df.copy()
        
        # Encode categorical features
        categorical_cols = ['company_size', 'industry']
        for col in categorical_cols:
            if col not in self.encoders:
                self.encoders[col] = LabelEncoder()
                df_processed[col] = self.encoders[col].fit_transform(df_processed[col])
            else:
                df_processed[col] = self.encoders[col].transform(df_processed[col])
        
        # Feature engineering
        df_processed['total_interactions'] = (
            df_processed['num_calls'] + 
            df_processed['num_emails'] + 
            df_processed['num_meetings']
        )
        
        df_processed['engagement_score'] = (
            df_processed['response_rate'] * 0.3 +
            df_processed['email_open_rate'] * 0.4 +
            (df_processed['page_views'] / 100) * 0.3
        )
        
        df_processed['recency_score'] = 1.0 / (1.0 + df_processed['days_since_interaction'] / 30.0)
        
        df_processed['lead_maturity'] = 1.0 / (1.0 + np.exp(-((df_processed['lead_age_days'] - 60) / 30.0)))
        
        # Select features for model
        feature_cols = [
            'company_size', 'budget', 'num_calls', 'num_emails', 'num_meetings',
            'response_rate', 'email_open_rate', 'page_views', 'lead_age_days',
            'priority_score', 'quality_score', 'total_interactions', 
            'engagement_score', 'recency_score', 'lead_maturity'
        ]
        
        self.feature_names = feature_cols
        
        return df_processed[feature_cols], df_processed['converted']
    
    def train(self, df_train=None):
        """
        Huấn luyện mô hình
        
        Args:
            df_train (DataFrame): Dữ liệu huấn luyện (nếu None, tạo dữ liệu mẫu)
            
        Returns:
            dict: Kết quả huấn luyện
        """
        print("=" * 80)
        print("HUẤN LUYỆN MÔ HÌNH PREDICTIVE LEAD SCORING")
        print("=" * 80)
        
        # Tạo dữ liệu mẫu nếu không có
        if df_train is None:
            print("\n[1/4] Tạo dữ liệu mẫu...")
            df_train = self.generate_sample_data(500)
            print(f"    ✓ Tạo {len(df_train)} mẫu dữ liệu")
        
        # Chuẩn bị features
        print("\n[2/4] Chuẩn bị features...")
        X, y = self.prepare_features(df_train)
        print(f"    ✓ {len(X)} mẫu với {len(X.columns)} features")
        print(f"    ✓ Phân bố nhãn: {y.value_counts().to_dict()}")
        
        # Chia dữ liệu train-test
        print("\n[3/4] Chia dữ liệu train/test...")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Chuẩn hóa features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        print(f"    ✓ Train set: {len(X_train)} mẫu")
        print(f"    ✓ Test set: {len(X_test)} mẫu")
        
        # Huấn luyện mô hình
        print("\n[4/4] Huấn luyện mô hình...")
        self.model = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42,
            verbose=0
        )
        self.model.fit(X_train_scaled, y_train)
        print("    ✓ Mô hình đã được huấn luyện")
        
        # Đánh giá
        print("\n" + "=" * 80)
        print("KẾT QUẢ ĐÁNH GIÁ")
        print("=" * 80)
        
        y_pred_train = self.model.predict(X_train_scaled)
        y_pred_test = self.model.predict(X_test_scaled)
        y_pred_proba = self.model.predict_proba(X_test_scaled)[:, 1]
        
        train_acc = accuracy_score(y_train, y_pred_train)
        test_acc = accuracy_score(y_test, y_pred_test)
        roc_auc = roc_auc_score(y_test, y_pred_proba)
        
        print(f"\nĐộ chính xác:")
        print(f"  - Train set: {train_acc:.4f} ({train_acc*100:.2f}%)")
        print(f"  - Test set:  {test_acc:.4f} ({test_acc*100:.2f}%)")
        print(f"  - ROC-AUC:   {roc_auc:.4f}")
        
        print(f"\nBáo cáo chi tiết:")
        print(classification_report(y_test, y_pred_test, 
                                   target_names=['Not Converted', 'Converted']))
        
        # Feature importance
        print(f"\nTầm quan trọng của features (Top 10):")
        feature_importance = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        for idx, row in feature_importance.head(10).iterrows():
            bar = '█' * int(row['importance'] * 100)
            print(f"  {row['feature']:25s} {bar} {row['importance']:.4f}")
        
        results = {
            'train_accuracy': train_acc,
            'test_accuracy': test_acc,
            'roc_auc': roc_auc,
            'feature_importance': feature_importance.to_dict('records'),
            'n_samples': len(df_train),
            'n_features': len(self.feature_names),
            'training_date': datetime.now().isoformat()
        }
        
        return results
    
    def save_model(self, model_name='lead_scoring_model'):
        """
        Lưu mô hình và các thành phần liên quan
        
        Args:
            model_name (str): Tên mô hình
        """
        if self.model is None:
            raise ValueError("Mô hình chưa được huấn luyện. Gọi train() trước.")
        
        print("\n" + "=" * 80)
        print("LƯU MÔ HÌNH")
        print("=" * 80)
        
        # Lưu mô hình chính
        model_file = os.path.join(self.model_path, f'{model_name}.pkl')
        joblib.dump(self.model, model_file)
        print(f"\n✓ Mô hình đã lưu: {model_file}")
        
        # Lưu scaler
        scaler_file = os.path.join(self.model_path, f'{model_name}_scaler.pkl')
        joblib.dump(self.scaler, scaler_file)
        print(f"✓ Scaler đã lưu: {scaler_file}")
        
        # Lưu encoders
        encoders_file = os.path.join(self.model_path, f'{model_name}_encoders.pkl')
        joblib.dump(self.encoders, encoders_file)
        print(f"✓ Encoders đã lưu: {encoders_file}")
        
        # Lưu feature names
        features_file = os.path.join(self.model_path, f'{model_name}_features.pkl')
        joblib.dump(self.feature_names, features_file)
        print(f"✓ Feature names đã lưu: {features_file}")
        
        print("\n" + "=" * 80)
        print("HOÀN THÀNH")
        print("=" * 80)
        
        return {
            'model_file': model_file,
            'scaler_file': scaler_file,
            'encoders_file': encoders_file,
            'features_file': features_file
        }
    
    def predict(self, X):
        """
        Dự đoán chất lượng lead
        
        Args:
            X (DataFrame): Dữ liệu cần dự đoán
            
        Returns:
            tuple: (predictions, probabilities)
        """
        if self.model is None:
            raise ValueError("Mô hình chưa được tải")
        
        X_processed = X.copy()
        
        # Encode categorical features
        for col in self.encoders:
            if col in X_processed.columns:
                X_processed[col] = self.encoders[col].transform(X_processed[col])
        
        # Chuẩn hóa
        X_scaled = self.scaler.transform(X_processed[self.feature_names])
        
        # Dự đoán
        predictions = self.model.predict(X_scaled)
        probabilities = self.model.predict_proba(X_scaled)[:, 1]
        
        return predictions, probabilities


def main():
    """Main function - Huấn luyện mô hình"""
    
    # Xác định đường dẫn model
    model_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Tạo trainer
    trainer = PredictiveLeadScoringTrainer(model_path=model_dir)
    
    # Huấn luyện mô hình
    results = trainer.train()
    
    # Lưu mô hình
    saved_files = trainer.save_model('lead_scoring_model')
    
    print("\n✅ MÔ HÌNH ĐÃ ĐƯỢC HUẤN LUYỆN VÀ LƯU THÀNH CÔNG")
    print(f"\nCác file đã lưu:")
    for key, value in saved_files.items():
        print(f"  - {key}: {value}")
    
    return trainer, results


if __name__ == '__main__':
    trainer, results = main()
