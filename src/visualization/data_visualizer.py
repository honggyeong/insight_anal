"""
대구 지역 장애인휠체어 급속충전기 및 보행로 데이터 시각화
고등학교 3학년 수준의 탐구를 위한 시각화 스크립트
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium import plugins
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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

class DaeguChargingStationVisualizer:
    """대구 지역 장애인휠체어 급속충전기 및 보행로 데이터 시각화 클래스"""
    
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
            self.charging_df = pd.read_csv(self.data_dir / "daegu_charging_stations.csv")
            self.walkway_df = pd.read_csv(self.data_dir / "daegu_walkways.csv")
            
            logger.info("대구 지역 데이터 로드 완료")
            
        except FileNotFoundError as e:
            logger.error(f"데이터 파일을 찾을 수 없습니다: {e}")
            raise
    
    def create_daegu_walkway_map(self, output_dir: str = "results"):
        """대구 지역 보행로 지도 생성"""
        if self.walkway_df is None:
            logger.error("보행로 데이터가 로드되지 않았습니다.")
            return
        
        # 대구 중심점
        center_lat = self.walkway_df['latitude'].mean()
        center_lon = self.walkway_df['longitude'].mean()
        
        # 지도 생성
        m = folium.Map(location=[center_lat, center_lon], zoom_start=12)
        
        # 보행로 타입별 색상 설정
        walkway_colors = {
            '보도블록': 'blue',
            '경사로': 'green',
            '엘리베이터': 'red',
            '육교': 'orange',
            '지하도': 'purple'
        }
        
        # 보행로 마커 추가
        for idx, row in self.walkway_df.iterrows():
            color = walkway_colors.get(row['walkway_type'], 'gray')
            
            # 휠체어 접근 가능 여부에 따른 아이콘 변경
            icon_type = 'check-circle' if row['wheelchair_accessible'] else 'times-circle'
            
            popup_text = f"""
            <b>{row['walkway_name']}</b><br>
            구: {row['district']}<br>
            타입: {row['walkway_type']}<br>
            폭: {row['width_meters']}m<br>
            길이: {row['length_meters']}m<br>
            휠체어 접근: {'가능' if row['wheelchair_accessible'] else '불가능'}<br>
            급속충전기 거리: {row['distance_to_charging']}m
            """
            
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=folium.Popup(popup_text, max_width=300),
                icon=folium.Icon(color=color, icon=icon_type)
            ).add_to(m)
        
        # 범례 추가
        legend_html = '''
        <div style="position: fixed; 
                    top: 10px; left: 50px; width: 200px; height: 150px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <p><b>대구 보행로 타입</b></p>
        '''
        
        for walkway_type, color in walkway_colors.items():
            legend_html += f'<p><i class="fa fa-road" style="color:{color}"></i> {walkway_type}</p>'
        
        legend_html += '''
        <p><i class="fa fa-check-circle" style="color:green"></i> 휠체어 접근 가능</p>
        <p><i class="fa fa-times-circle" style="color:red"></i> 휠체어 접근 불가</p>
        </div>
        '''
        
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # 지도 저장
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        m.save(output_path / 'daegu_walkway_map.html')
        
        logger.info(f"대구 보행로 지도 생성 완료: {output_path / 'daegu_walkway_map.html'}")
    
    def create_daegu_charging_distribution_map(self, output_dir: str = "results"):
        """대구 지역 급속충전기 분포 지도 (색상으로 밀도 표시)"""
        if self.charging_df is None:
            logger.error("급속충전기 데이터가 로드되지 않았습니다.")
            return
        
        # 대구 중심점
        center_lat = self.charging_df['latitude'].mean()
        center_lon = self.charging_df['longitude'].mean()
        
        # 지도 생성
        m = folium.Map(location=[center_lat, center_lon], zoom_start=12)
        
        # 구별 급속충전기 수 계산
        district_counts = self.charging_df['district'].value_counts()
        max_count = district_counts.max()
        
        # 구별 색상 설정 (밀도에 따라)
        district_colors = {}
        for district in district_counts.index:
            ratio = district_counts[district] / max_count
            if ratio > 0.8:
                color = 'red'
            elif ratio > 0.6:
                color = 'orange'
            elif ratio > 0.4:
                color = 'yellow'
            else:
                color = 'green'
            district_colors[district] = color
        
        # 급속충전기 마커 추가
        for idx, row in self.charging_df.iterrows():
            district = row['district']
            color = district_colors.get(district, 'gray')
            
            # 접근성 점수에 따른 아이콘 크기 조정
            icon_size = 15 if row['accessibility_score'] > 0.8 else 10
            
            popup_text = f"""
            <b>{row['station_name']}</b><br>
            구: {row['district']}<br>
            타입: {row['charging_type']}<br>
            주소: {row['address']}<br>
            접근성 점수: {row['accessibility_score']:.2f}<br>
            보행로 근처: {'예' if row['near_walkway'] else '아니오'}
            """
            
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=icon_size,
                popup=folium.Popup(popup_text, max_width=300),
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.7
            ).add_to(m)
        
        # 구별 밀도 범례 추가
        legend_html = '''
        <div style="position: fixed; 
                    top: 10px; right: 50px; width: 200px; height: 200px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <p><b>대구 구별 급속충전기 밀도</b></p>
        '''
        
        for district, count in district_counts.items():
            color = district_colors.get(district, 'gray')
            legend_html += f'<p><i class="fa fa-circle" style="color:{color}"></i> {district}: {count}개</p>'
        
        legend_html += '''
        <p><b>밀도 기준:</b></p>
        <p><i class="fa fa-circle" style="color:red"></i> 높음 (80% 이상)</p>
        <p><i class="fa fa-circle" style="color:orange"></i> 중상 (60-80%)</p>
        <p><i class="fa fa-circle" style="color:yellow"></i> 중하 (40-60%)</p>
        <p><i class="fa fa-circle" style="color:green"></i> 낮음 (40% 미만)</p>
        </div>
        '''
        
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # 지도 저장
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        m.save(output_path / 'daegu_charging_distribution_map.html')
        
        logger.info(f"대구 급속충전기 분포 지도 생성 완료: {output_path / 'daegu_charging_distribution_map.html'}")
    
    def create_daegu_combined_map(self, output_dir: str = "results"):
        """대구 지역 보행로와 급속충전기 통합 지도"""
        if self.walkway_df is None or self.charging_df is None:
            logger.error("데이터가 로드되지 않았습니다.")
            return
        
        # 대구 중심점
        center_lat = (self.walkway_df['latitude'].mean() + self.charging_df['latitude'].mean()) / 2
        center_lon = (self.walkway_df['longitude'].mean() + self.charging_df['longitude'].mean()) / 2
        
        # 지도 생성
        m = folium.Map(location=[center_lat, center_lon], zoom_start=12)
        
        # 보행로 마커 추가 (파란색 계열)
        for idx, row in self.walkway_df.iterrows():
            color = 'blue' if row['wheelchair_accessible'] else 'lightblue'
            
            popup_text = f"""
            <b>{row['walkway_name']}</b><br>
            구: {row['district']}<br>
            타입: {row['walkway_type']}<br>
            휠체어 접근: {'가능' if row['wheelchair_accessible'] else '불가능'}
            """
            
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=8,
                popup=folium.Popup(popup_text, max_width=300),
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.6
            ).add_to(m)
        
        # 급속충전기 마커 추가 (빨간색 계열)
        for idx, row in self.charging_df.iterrows():
            color = 'red' if row['near_walkway'] else 'orange'
            
            popup_text = f"""
            <b>{row['station_name']}</b><br>
            구: {row['district']}<br>
            타입: {row['charging_type']}<br>
            접근성 점수: {row['accessibility_score']:.2f}
            """
            
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=12,
                popup=folium.Popup(popup_text, max_width=300),
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.8
            ).add_to(m)
        
        # 범례 추가
        legend_html = '''
        <div style="position: fixed; 
                    top: 10px; left: 50px; width: 250px; height: 180px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <p><b>대구 보행로 & 급속충전기</b></p>
        <p><i class="fa fa-circle" style="color:blue"></i> 보행로 (휠체어 접근 가능)</p>
        <p><i class="fa fa-circle" style="color:lightblue"></i> 보행로 (휠체어 접근 불가)</p>
        <p><i class="fa fa-circle" style="color:red"></i> 급속충전기 (보행로 근처)</p>
        <p><i class="fa fa-circle" style="color:orange"></i> 급속충전기 (보행로 멀리)</p>
        </div>
        '''
        
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # 지도 저장
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        m.save(output_path / 'daegu_combined_map.html')
        
        logger.info(f"대구 통합 지도 생성 완료: {output_path / 'daegu_combined_map.html'}")
    
    def create_daegu_district_analysis(self, output_dir: str = "results"):
        """대구 구별 분석 시각화"""
        if self.charging_df is None or self.walkway_df is None:
            logger.error("데이터가 로드되지 않았습니다.")
            return
        
        # 구별 통계 계산
        charging_by_district = self.charging_df.groupby('district').agg({
            'station_id': 'count',
            'accessibility_score': 'mean',
            'near_walkway': 'sum'
        }).rename(columns={
            'station_id': '급속충전기_수',
            'accessibility_score': '평균_접근성_점수',
            'near_walkway': '보행로_근처_수'
        })
        
        walkway_by_district = self.walkway_df.groupby('district').agg({
            'walkway_id': 'count',
            'wheelchair_accessible': 'sum'
        }).rename(columns={
            'walkway_id': '보행로_수',
            'wheelchair_accessible': '휠체어_접근_가능_수'
        })
        
        # 통합 통계
        district_stats = charging_by_district.join(walkway_by_district)
        district_stats['보행로_근처_비율'] = (district_stats['보행로_근처_수'] / district_stats['급속충전기_수'] * 100).round(2)
        district_stats['휠체어_접근_비율'] = (district_stats['휠체어_접근_가능_수'] / district_stats['보행로_수'] * 100).round(2)
        
        # 시각화
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. 구별 급속충전기 수
        axes[0, 0].bar(district_stats.index, district_stats['급속충전기_수'], color='red', alpha=0.7)
        axes[0, 0].set_title('대구 구별 급속충전기 수', fontsize=14)
        axes[0, 0].set_ylabel('개수')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # 2. 구별 보행로 수
        axes[0, 1].bar(district_stats.index, district_stats['보행로_수'], color='blue', alpha=0.7)
        axes[0, 1].set_title('대구 구별 보행로 수', fontsize=14)
        axes[0, 1].set_ylabel('개수')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # 3. 구별 평균 접근성 점수
        axes[1, 0].bar(district_stats.index, district_stats['평균_접근성_점수'], color='green', alpha=0.7)
        axes[1, 0].set_title('대구 구별 평균 접근성 점수', fontsize=14)
        axes[1, 0].set_ylabel('접근성 점수')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # 4. 구별 휠체어 접근 가능 비율
        axes[1, 1].bar(district_stats.index, district_stats['휠체어_접근_비율'], color='orange', alpha=0.7)
        axes[1, 1].set_title('대구 구별 휠체어 접근 가능 비율', fontsize=14)
        axes[1, 1].set_ylabel('비율 (%)')
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        # 저장
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        plt.savefig(output_path / 'daegu_district_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"대구 구별 분석 시각화 완료: {output_path / 'daegu_district_analysis.png'}")
        
        return district_stats
    
    def generate_all_visualizations(self, output_dir: str = "results"):
        """모든 시각화 생성"""
        logger.info("대구 지역 시각화 생성 시작...")
        
        # 데이터 로드
        self.load_data()
        
        # 각종 시각화 생성
        self.create_daegu_walkway_map(output_dir)
        self.create_daegu_charging_distribution_map(output_dir)
        self.create_daegu_combined_map(output_dir)
        district_stats = self.create_daegu_district_analysis(output_dir)
        
        logger.info("대구 지역 모든 시각화 생성 완료!")
        return district_stats

def main():
    """메인 실행 함수"""
    logger.info("대구 지역 장애인휠체어 급속충전기 시각화 시작")
    
    try:
        # 시각화기 초기화
        visualizer = DaeguChargingStationVisualizer()
        
        # 모든 시각화 생성
        district_stats = visualizer.generate_all_visualizations()
        
        print("대구 지역 시각화 생성 완료!")
        print("\n=== 대구 구별 분석 결과 ===")
        print(district_stats)
        
    except Exception as e:
        logger.error(f"시각화 중 오류 발생: {e}")
        raise

if __name__ == "__main__":
    main() 