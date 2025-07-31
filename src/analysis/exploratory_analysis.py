"""
장애인휠체어 급속충전기 접근성 분석
고등학교 3학년 수준의 탐구적 데이터 분석
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple
import logging
from pathlib import Path
import matplotlib.font_manager as fm

# 한글 폰트 설정
plt.rcParams['font.family'] = ['AppleGothic', 'DejaVu Sans', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 한글 폰트가 없을 경우를 대비한 폰트 설정
try:
    # AppleGothic 폰트 확인
    font_path = '/System/Library/Fonts/AppleGothic.ttf'
    if Path(font_path).exists():
        font_prop = fm.FontProperties(fname=font_path)
        plt.rcParams['font.family'] = font_prop.get_name()
    else:
        # 대체 폰트들 시도
        fallback_fonts = ['Arial Unicode MS', 'Malgun Gothic', 'NanumGothic']
        for font in fallback_fonts:
            try:
                fm.findfont(font)
                plt.rcParams['font.family'] = font
                break
            except:
                continue
except:
    # 폰트 설정 실패 시 기본 설정 유지
    plt.rcParams['font.family'] = 'DejaVu Sans'

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChargingStationAnalyzer:
    """장애인휠체어 급속충전기 접근성 분석 클래스"""
    
    def __init__(self, data_dir: str = "data"):
        """
        Args:
            data_dir (str): 데이터 파일이 저장된 디렉토리 경로
        """
        self.data_dir = Path(data_dir)
        self.charging_df = None
        self.walkway_df = None
        
    def load_data(self):
        """데이터 로드"""
        try:
            self.charging_df = pd.read_csv(self.data_dir / "charging_stations.csv")
            self.walkway_df = pd.read_csv(self.data_dir / "walkways.csv")
            
            logger.info("데이터 로드 완료")
            
        except FileNotFoundError as e:
            logger.error(f"데이터 파일을 찾을 수 없습니다: {e}")
            raise
    
    def basic_statistics(self) -> Dict:
        """기본 통계 분석"""
        if self.charging_df is None or self.walkway_df is None:
            logger.error("데이터가 로드되지 않았습니다.")
            return {}
        
        stats = {
            '총_급속충전기_수': len(self.charging_df),
            '총_보행로_수': len(self.walkway_df),
            '보행로_근처_급속충전기_수': self.charging_df['near_walkway'].sum(),
            '급속충전기_근처_보행로_수': self.walkway_df['near_charging_station'].sum(),
            '도시별_급속충전기_수': self.charging_df['city'].value_counts().to_dict(),
            '보행로_타입별_분포': self.walkway_df['walkway_type'].value_counts().to_dict()
        }
        
        return stats
    
    def analyze_regional_distribution(self) -> pd.DataFrame:
        """지역별 분포 분석"""
        if self.charging_df is None:
            return pd.DataFrame()
        
        # 도시별 급속충전기 밀도 분석
        city_stats = self.charging_df.groupby('city').agg({
            'station_id': 'count',
            'accessibility_score': 'mean',
            'near_walkway': 'sum'
        }).rename(columns={
            'station_id': '급속충전기_수',
            'accessibility_score': '평균_접근성_점수',
            'near_walkway': '보행로_근처_수'
        })
        
        city_stats['보행로_근처_비율'] = (city_stats['보행로_근처_수'] / city_stats['급속충전기_수'] * 100).round(2)
        
        return city_stats
    
    def analyze_walkway_accessibility(self) -> pd.DataFrame:
        """보행로 접근성 분석"""
        if self.walkway_df is None:
            return pd.DataFrame()
        
        # 보행로 타입별 접근성 분석
        walkway_stats = self.walkway_df.groupby('walkway_type').agg({
            'walkway_id': 'count',
            'wheelchair_accessible': 'sum',
            'near_charging_station': 'sum',
            'distance_to_charging': 'mean'
        }).rename(columns={
            'walkway_id': '보행로_수',
            'wheelchair_accessible': '휠체어_접근_가능_수',
            'near_charging_station': '급속충전기_근처_수',
            'distance_to_charging': '평균_거리_미터'
        })
        
        walkway_stats['휠체어_접근_비율'] = (walkway_stats['휠체어_접근_가능_수'] / walkway_stats['보행로_수'] * 100).round(2)
        walkway_stats['급속충전기_근처_비율'] = (walkway_stats['급속충전기_근처_수'] / walkway_stats['보행로_수'] * 100).round(2)
        
        return walkway_stats
    
    def calculate_accessibility_index(self) -> pd.DataFrame:
        """접근성 지수 계산"""
        if self.charging_df is None or self.walkway_df is None:
            return pd.DataFrame()
        
        # 도시별 접근성 지수 계산
        city_accessibility = self.charging_df.groupby('city').agg({
            'accessibility_score': 'mean',
            'near_walkway': 'sum',
            'station_id': 'count'
        })
        
        city_accessibility['접근성_지수'] = (
            city_accessibility['accessibility_score'] * 0.4 +
            (city_accessibility['near_walkway'] / city_accessibility['station_id']) * 0.6
        ).round(3)
        
        return city_accessibility
    
    def create_visualizations(self, output_dir: str = "results"):
        """시각화 생성"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        if self.charging_df is None or self.walkway_df is None:
            logger.error("데이터가 로드되지 않았습니다.")
            return
        
        # 1. 도시별 급속충전기 분포
        plt.figure(figsize=(12, 6))
        city_counts = self.charging_df['city'].value_counts()
        plt.bar(city_counts.index, city_counts.values, color='skyblue')
        plt.title('도시별 장애인휠체어 급속충전기 분포', fontsize=15)
        plt.xlabel('도시')
        plt.ylabel('급속충전기 수')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(output_path / 'city_charging_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. 보행로 타입별 분포
        plt.figure(figsize=(10, 6))
        walkway_counts = self.walkway_df['walkway_type'].value_counts()
        plt.pie(walkway_counts.values, labels=walkway_counts.index, autopct='%1.1f%%')
        plt.title('보행로 타입별 분포', fontsize=15)
        plt.tight_layout()
        plt.savefig(output_path / 'walkway_type_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. 접근성 점수 분포
        plt.figure(figsize=(10, 6))
        plt.hist(self.charging_df['accessibility_score'], bins=20, color='lightgreen', alpha=0.7)
        plt.title('급속충전기 접근성 점수 분포', fontsize=15)
        plt.xlabel('접근성 점수')
        plt.ylabel('빈도')
        plt.tight_layout()
        plt.savefig(output_path / 'accessibility_score_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 4. 보행로-급속충전기 거리 분석
        plt.figure(figsize=(10, 6))
        plt.scatter(self.walkway_df['distance_to_charging'], 
                   self.walkway_df['width_meters'], 
                   alpha=0.6, c='orange')
        plt.title('보행로 폭과 급속충전기 거리의 관계', fontsize=15)
        plt.xlabel('급속충전기까지 거리 (미터)')
        plt.ylabel('보행로 폭 (미터)')
        plt.tight_layout()
        plt.savefig(output_path / 'walkway_charging_distance.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info("시각화 생성 완료")
    
    def generate_report(self, output_dir: str = "results"):
        """분석 리포트 생성"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # 기본 통계
        stats = self.basic_statistics()
        regional_stats = self.analyze_regional_distribution()
        walkway_stats = self.analyze_walkway_accessibility()
        accessibility_index = self.calculate_accessibility_index()
        
        # 리포트 작성
        report = f"""
# 장애인휠체어 급속충전기 접근성 분석 리포트

## 1. 기본 현황
- 총 급속충전기 수: {stats['총_급속충전기_수']}개
- 총 보행로 수: {stats['총_보행로_수']}개
- 보행로 근처 급속충전기: {stats['보행로_근처_급속충전기_수']}개 ({stats['보행로_근처_급속충전기_수']/stats['총_급속충전기_수']*100:.1f}%)
- 급속충전기 근처 보행로: {stats['급속충전기_근처_보행로_수']}개 ({stats['급속충전기_근처_보행로_수']/stats['총_보행로_수']*100:.1f}%)

## 2. 지역별 분석
{regional_stats.to_string()}

## 3. 보행로 접근성 분석
{walkway_stats.to_string()}

## 4. 접근성 지수
{accessibility_index.to_string()}

## 5. 탐구 결과 및 제언

### 주요 발견사항:
1. 도시별로 급속충전기 분포에 차이가 있음
2. 보행로 타입별로 휠체어 접근성에 차이가 있음
3. 급속충전기와 보행로 간의 거리가 접근성에 영향을 미침

### 개선 제언:
1. 접근성이 낮은 지역에 급속충전기 추가 설치
2. 보행로 정비와 함께 급속충전기 설치 계획 수립
3. 지역별 접근성 격차 해소를 위한 정책 수립
        """
        
        with open(output_path / 'charging_station_analysis_report.md', 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info("분석 리포트 생성 완료")
        return report

def main():
    """메인 실행 함수"""
    logger.info("장애인휠체어 급속충전기 접근성 분석 시작")
    
    try:
        # 분석기 초기화
        analyzer = ChargingStationAnalyzer()
        
        # 데이터 로드
        analyzer.load_data()
        
        # 기본 통계 출력
        stats = analyzer.basic_statistics()
        print("\n=== 기본 통계 ===")
        for key, value in stats.items():
            if isinstance(value, dict):
                print(f"{key}:")
                for k, v in value.items():
                    print(f"  {k}: {v}")
            else:
                print(f"{key}: {value}")
        
        # 지역별 분석
        regional_stats = analyzer.analyze_regional_distribution()
        print("\n=== 지역별 분석 ===")
        print(regional_stats)
        
        # 보행로 접근성 분석
        walkway_stats = analyzer.analyze_walkway_accessibility()
        print("\n=== 보행로 접근성 분석 ===")
        print(walkway_stats)
        
        # 시각화 생성
        analyzer.create_visualizations()
        
        # 리포트 생성
        analyzer.generate_report()
        
        logger.info("분석 완료!")
        
    except Exception as e:
        logger.error(f"분석 중 오류 발생: {e}")
        raise

if __name__ == "__main__":
    main() 