"""
휠체어 이용자를 위한 최적 경로 예측 모델
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib
from typing import Dict, List, Tuple, Optional
import logging
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WheelchairRoutePredictor:
    """휠체어 이용자를 위한 경로 예측 모델"""
    
    def __init__(self, data_dir: str = "../data"):
        """
        Args:
            data_dir (str): 데이터 파일이 저장된 디렉토리 경로
        """
        self.data_dir = Path(data_dir)
        self.facilities_df = None
        self.road_df = None
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_columns = []
        
    def load_data(self):
        """데이터 로드"""
        try:
            self.facilities_df = pd.read_csv(self.data_dir / "wheelchair_facilities.csv")
            self.road_df = pd.read_csv(self.data_dir / "road_accessibility.csv")
            
            logger.info("데이터 로드 완료")
            logger.info(f"편의시설: {len(self.facilities_df)}건")
            logger.info(f"도로 접근성: {len(self.road_df)}건")
            
        except FileNotFoundError as e:
            logger.error(f"데이터 파일을 찾을 수 없습니다: {e}")
            raise
    
    def create_training_data(self) -> pd.DataFrame:
        """모델 학습을 위한 데이터 생성"""
        # 도로 데이터를 기반으로 휠체어 접근성 점수 계산
        training_data = self.road_df.copy()
        
        # 특성 엔지니어링
        training_data['accessibility_score'] = self._calculate_road_accessibility(training_data)
        training_data['facility_density'] = self._calculate_facility_density(training_data)
        training_data['route_quality'] = self._calculate_route_quality(training_data)
        
        # 범주형 변수 인코딩
        categorical_columns = ['road_type', 'surface_condition', 'maintenance_status']
        for col in categorical_columns:
            if col in training_data.columns:
                le = LabelEncoder()
                training_data[f'{col}_encoded'] = le.fit_transform(training_data[col])
                self.label_encoders[col] = le
        
        # 수치형 특성 선택
        self.feature_columns = [
            'width_meters', 'slope_degrees', 'facility_density', 'route_quality',
            'road_type_encoded', 'surface_condition_encoded', 'maintenance_status_encoded'
        ]
        
        return training_data
    
    def _calculate_road_accessibility(self, df: pd.DataFrame) -> pd.Series:
        """도로 접근성 점수 계산"""
        # 폭 점수 (1.5m 이상이면 좋음)
        width_score = np.where(df['width_meters'] >= 1.5, 1.0, 
                              df['width_meters'] / 1.5)
        
        # 경사도 점수 (5도 이하면 좋음)
        slope_score = np.where(df['slope_degrees'] <= 5, 1.0,
                              np.maximum(0, 1 - (df['slope_degrees'] - 5) / 10))
        
        # 종합 접근성 점수
        accessibility_score = (width_score * 0.4 + slope_score * 0.6)
        
        return accessibility_score
    
    def _calculate_facility_density(self, df: pd.DataFrame) -> pd.Series:
        """주변 편의시설 밀도 계산"""
        if self.facilities_df is None:
            return pd.Series(0, index=df.index)
        
        facility_density = []
        
        for idx, road in df.iterrows():
            # 도로 위치에서 1km 반경 내 편의시설 개수 계산
            road_lat, road_lon = road['latitude'], road['longitude']
            
            # 간단한 유클리드 거리 계산 (실제로는 Haversine 공식 사용 권장)
            distances = np.sqrt(
                (self.facilities_df['latitude'] - road_lat) ** 2 +
                (self.facilities_df['longitude'] - road_lon) ** 2
            )
            
            # 1km 반경 내 편의시설 개수 (대략적인 계산)
            nearby_facilities = len(distances[distances < 0.01])  # 약 1km
            facility_density.append(nearby_facilities)
        
        return pd.Series(facility_density, index=df.index)
    
    def _calculate_route_quality(self, df: pd.DataFrame) -> pd.Series:
        """경로 품질 점수 계산"""
        # 표면 상태에 따른 점수
        surface_scores = {
            '양호': 1.0,
            '보통': 0.7,
            '불량': 0.3
        }
        
        # 유지보수 상태에 따른 점수
        maintenance_scores = {
            '정상': 1.0,
            '점검중': 0.5,
            '보수예정': 0.3
        }
        
        surface_score = df['surface_condition'].map(surface_scores).fillna(0.5)
        maintenance_score = df['maintenance_status'].map(maintenance_scores).fillna(0.5)
        
        # 종합 품질 점수
        route_quality = (surface_score * 0.6 + maintenance_score * 0.4)
        
        return route_quality
    
    def train_model(self, test_size: float = 0.2, random_state: int = 42):
        """모델 학습"""
        # 학습 데이터 생성
        training_data = self.create_training_data()
        
        # 특성과 타겟 분리
        X = training_data[self.feature_columns]
        y = training_data['accessibility_score']
        
        # 데이터 분할
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        # 특성 스케일링
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # 모델 선택 및 학습
        models = {
            'RandomForest': RandomForestRegressor(n_estimators=100, random_state=random_state),
            'GradientBoosting': GradientBoostingRegressor(n_estimators=100, random_state=random_state)
        }
        
        best_model = None
        best_score = -np.inf
        
        for name, model in models.items():
            logger.info(f"{name} 모델 학습 중...")
            
            # 교차 검증
            cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='r2')
            logger.info(f"{name} 교차 검증 R² 점수: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
            
            # 모델 학습
            model.fit(X_train_scaled, y_train)
            
            # 테스트 세트 평가
            y_pred = model.predict(X_test_scaled)
            r2 = r2_score(y_test, y_pred)
            mse = mean_squared_error(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            
            logger.info(f"{name} 테스트 성능:")
            logger.info(f"  R² 점수: {r2:.4f}")
            logger.info(f"  MSE: {mse:.4f}")
            logger.info(f"  MAE: {mae:.4f}")
            
            if r2 > best_score:
                best_score = r2
                best_model = model
        
        self.model = best_model
        logger.info(f"최적 모델 선택: {type(best_model).__name__}")
        
        return {
            'X_test': X_test,
            'y_test': y_test,
            'y_pred': best_model.predict(X_test_scaled),
            'feature_importance': pd.DataFrame({
                'feature': self.feature_columns,
                'importance': best_model.feature_importances_
            }).sort_values('importance', ascending=False)
        }
    
    def predict_route_accessibility(self, route_data: pd.DataFrame) -> np.ndarray:
        """경로 접근성 예측"""
        if self.model is None:
            raise ValueError("모델이 학습되지 않았습니다. train_model()을 먼저 실행하세요.")
        
        # 데이터 전처리
        processed_data = self._preprocess_route_data(route_data)
        
        # 특성 스케일링
        X_scaled = self.scaler.transform(processed_data[self.feature_columns])
        
        # 예측
        predictions = self.model.predict(X_scaled)
        
        return predictions
    
    def _preprocess_route_data(self, route_data: pd.DataFrame) -> pd.DataFrame:
        """경로 데이터 전처리"""
        processed_data = route_data.copy()
        
        # 편의시설 밀도 계산
        processed_data['facility_density'] = self._calculate_facility_density(processed_data)
        
        # 경로 품질 계산
        processed_data['route_quality'] = self._calculate_route_quality(processed_data)
        
        # 범주형 변수 인코딩
        for col, le in self.label_encoders.items():
            if col in processed_data.columns:
                processed_data[f'{col}_encoded'] = le.transform(processed_data[col])
        
        return processed_data
    
    def save_model(self, model_path: str = "../models"):
        """모델 저장"""
        model_dir = Path(model_path)
        model_dir.mkdir(exist_ok=True)
        
        # 모델 저장
        joblib.dump(self.model, model_dir / "wheelchair_route_model.pkl")
        
        # 스케일러 저장
        joblib.dump(self.scaler, model_dir / "wheelchair_route_scaler.pkl")
        
        # 라벨 인코더 저장
        joblib.dump(self.label_encoders, model_dir / "wheelchair_route_encoders.pkl")
        
        # 특성 컬럼 저장
        joblib.dump(self.feature_columns, model_dir / "wheelchair_route_features.pkl")
        
        logger.info(f"모델 저장 완료: {model_dir}")
    
    def load_model(self, model_path: str = "../models"):
        """모델 로드"""
        model_dir = Path(model_path)
        
        self.model = joblib.load(model_dir / "wheelchair_route_model.pkl")
        self.scaler = joblib.load(model_dir / "wheelchair_route_scaler.pkl")
        self.label_encoders = joblib.load(model_dir / "wheelchair_route_encoders.pkl")
        self.feature_columns = joblib.load(model_dir / "wheelchair_route_features.pkl")
        
        logger.info("모델 로드 완료")
    
    def get_optimal_route(self, start_point: Tuple[float, float], 
                         end_point: Tuple[float, float], 
                         route_candidates: List[Dict]) -> Dict:
        """최적 경로 선택"""
        if self.model is None:
            raise ValueError("모델이 로드되지 않았습니다.")
        
        # 경로 후보들의 접근성 점수 예측
        route_scores = []
        
        for route in route_candidates:
            # 경로 데이터를 데이터프레임으로 변환
            route_df = pd.DataFrame([route])
            
            # 접근성 점수 예측
            accessibility_score = self.predict_route_accessibility(route_df)[0]
            
            route_scores.append({
                'route': route,
                'accessibility_score': accessibility_score,
                'estimated_time': route.get('estimated_time', 0),
                'distance': route.get('distance', 0)
            })
        
        # 종합 점수 계산 (접근성 60%, 시간 25%, 거리 15%)
        for route_info in route_scores:
            accessibility_weight = 0.6
            time_weight = 0.25
            distance_weight = 0.15
            
            # 정규화된 점수 계산
            max_time = max(r['estimated_time'] for r in route_scores)
            max_distance = max(r['distance'] for r in route_scores)
            
            time_score = 1 - (route_info['estimated_time'] / max_time) if max_time > 0 else 0
            distance_score = 1 - (route_info['distance'] / max_distance) if max_distance > 0 else 0
            
            route_info['total_score'] = (
                route_info['accessibility_score'] * accessibility_weight +
                time_score * time_weight +
                distance_score * distance_weight
            )
        
        # 최적 경로 선택
        optimal_route = max(route_scores, key=lambda x: x['total_score'])
        
        return optimal_route

def create_sample_route_data():
    """샘플 경로 데이터 생성"""
    sample_routes = []
    
    for i in range(10):
        route = {
            'road_type': np.random.choice(['보도블록', '경사로', '엘리베이터']),
            'width_meters': round(np.random.uniform(1.0, 3.0), 1),
            'slope_degrees': round(np.random.uniform(0, 15), 1),
            'surface_condition': np.random.choice(['양호', '보통', '불량']),
            'maintenance_status': np.random.choice(['정상', '점검중', '보수예정']),
            'latitude': 37.5665 + np.random.uniform(-0.01, 0.01),
            'longitude': 126.9780 + np.random.uniform(-0.01, 0.01),
            'estimated_time': np.random.randint(5, 30),
            'distance': round(np.random.uniform(100, 1000), 0)
        }
        sample_routes.append(route)
    
    return sample_routes

def main():
    """메인 실행 함수"""
    predictor = WheelchairRoutePredictor()
    
    try:
        # 데이터 로드
        predictor.load_data()
        
        # 모델 학습
        logger.info("모델 학습 시작...")
        results = predictor.train_model()
        
        # 특성 중요도 출력
        print("\n=== 특성 중요도 ===")
        print(results['feature_importance'])
        
        # 모델 저장
        predictor.save_model()
        
        # 샘플 경로 예측 테스트
        sample_routes = create_sample_route_data()
        start_point = (37.5665, 126.9780)
        end_point = (37.5665, 126.9880)
        
        optimal_route = predictor.get_optimal_route(start_point, end_point, sample_routes)
        
        print("\n=== 최적 경로 선택 결과 ===")
        print(f"접근성 점수: {optimal_route['accessibility_score']:.4f}")
        print(f"예상 소요시간: {optimal_route['estimated_time']}분")
        print(f"거리: {optimal_route['distance']}m")
        print(f"종합 점수: {optimal_route['total_score']:.4f}")
        
        print("\n모델 학습 및 테스트 완료!")
        
    except Exception as e:
        logger.error(f"모델 학습 중 오류 발생: {e}")
        raise

if __name__ == "__main__":
    main() 