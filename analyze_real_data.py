"""
실제 공공데이터포털 데이터 분석 스크립트
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
from datetime import datetime
import folium
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정
plt.rcParams['font.family'] = ['AppleGothic', 'Arial Unicode MS', 'Malgun Gothic', 'NanumGothic']
plt.rcParams['axes.unicode_minus'] = False

def load_real_data():
    """실제 데이터 로드"""
    print("실제 데이터 로드 중...")
    
    try:
        # 다양한 인코딩 시도
        encodings = ['utf-8', 'cp949', 'euc-kr', 'latin1']
        
        for encoding in encodings:
            try:
                charging_df = pd.read_csv('data/전국전동휠체어급속충전기표준데이터.csv', encoding=encoding)
                print(f"급속충전기 데이터 로드 성공 (인코딩: {encoding})")
                print(f"데이터 크기: {charging_df.shape}")
                print(f"컬럼명: {list(charging_df.columns)}")
                break
            except UnicodeDecodeError:
                continue
        else:
            print("모든 인코딩 시도 실패")
            return None, None
            
        # 교통약자 이동지원센터 데이터도 로드
        try:
            support_df = pd.read_csv('data/전국교통약자이동지원센터정보표준데이터.csv', encoding=encoding)
            print(f"교통약자 이동지원센터 데이터 로드 성공")
            print(f"데이터 크기: {support_df.shape}")
            print(f"컬럼명: {list(support_df.columns)}")
        except:
            print("교통약자 이동지원센터 데이터 로드 실패")
            support_df = None
            
        return charging_df, support_df
        
    except Exception as e:
        print(f"데이터 로드 오류: {e}")
        return None, None

def analyze_charging_data(df):
    """급속충전기 데이터 분석"""
    if df is None:
        return
        
    print("\n=== 급속충전기 데이터 분석 ===")
    
    # 기본 정보
    print(f"총 급속충전기 수: {len(df)}")
    
    # 컬럼명 확인 및 정리
    print("\n컬럼명:")
    for i, col in enumerate(df.columns):
        print(f"{i+1}. {col}")
    
    # 첫 몇 행 확인
    print("\n첫 3행 데이터:")
    print(df.head(3))
    
    # 데이터 타입 확인
    print("\n데이터 타입:")
    print(df.dtypes)
    
    # 결측값 확인
    print("\n결측값 개수:")
    print(df.isnull().sum())
    
    # 지역별 분포 분석
    if len(df.columns) > 1:
        region_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]
        print(f"\n지역별 분포 ({region_col}):")
        region_counts = df[region_col].value_counts()
        print(region_counts.head(10))
        
        # 대구 지역 필터링
        daegu_data = df[df[region_col].str.contains('대구', na=False)]
        print(f"\n대구 지역 급속충전기 수: {len(daegu_data)}")
        
        if len(daegu_data) > 0:
            print("\n대구 지역 상세 정보:")
            print(daegu_data.head())
    
    # 좌표 정보 확인
    lat_cols = [col for col in df.columns if '위도' in col or 'latitude' in col.lower()]
    lon_cols = [col for col in df.columns if '경도' in col or 'longitude' in col.lower()]
    
    if lat_cols and lon_cols:
        print(f"\n위도 컬럼: {lat_cols}")
        print(f"경도 컬럼: {lon_cols}")
        
        # 좌표 데이터 확인
        lat_col = lat_cols[0]
        lon_col = lon_cols[0]
        
        print(f"\n위도 범위: {df[lat_col].min()} ~ {df[lat_col].max()}")
        print(f"경도 범위: {df[lon_col].min()} ~ {df[lon_col].max()}")
        
        # 유효한 좌표만 필터링
        valid_coords = df.dropna(subset=[lat_col, lon_col])
        print(f"유효한 좌표 데이터: {len(valid_coords)}개")

def analyze_support_data(df):
    """교통약자 이동지원센터 데이터 분석"""
    if df is None:
        return
        
    print("\n=== 교통약자 이동지원센터 데이터 분석 ===")
    
    print(f"총 센터 수: {len(df)}")
    
    # 컬럼명 확인
    print("\n컬럼명:")
    for i, col in enumerate(df.columns):
        print(f"{i+1}. {col}")
    
    # 첫 몇 행 확인
    print("\n첫 3행 데이터:")
    print(df.head(3))

def create_visualizations(charging_df, support_df):
    """시각화 생성"""
    print("\n=== 시각화 생성 ===")
    
    # 1. 전국 급속충전기 분포 지도
    if charging_df is not None and len(charging_df.columns) > 2:
        try:
            # 좌표 컬럼 찾기
            lat_cols = [col for col in charging_df.columns if '위도' in col or 'latitude' in col.lower()]
            lon_cols = [col for col in charging_df.columns if '경도' in col or 'longitude' in col.lower()]
            
            if lat_cols and lon_cols:
                lat_col = lat_cols[0]
                lon_col = lon_cols[0]
                
                # 유효한 좌표만 필터링
                valid_data = charging_df.dropna(subset=[lat_col, lon_col])
                
                if len(valid_data) > 0:
                    # 한국 중심 좌표
                    center_lat = valid_data[lat_col].mean()
                    center_lon = valid_data[lon_col].mean()
                    
                    # 지도 생성
                    m = folium.Map(location=[center_lat, center_lon], zoom_start=7)
                    
                    # 급속충전기 마커 추가
                    for idx, row in valid_data.head(100).iterrows():  # 처음 100개만
                        folium.Marker(
                            location=[row[lat_col], row[lon_col]],
                            popup=f"급속충전기: {row.iloc[0] if len(row) > 0 else 'N/A'}",
                            icon=folium.Icon(color='red', icon='info-sign')
                        ).add_to(m)
                    
                    # 지도 저장
                    m.save('results/전국_급속충전기_분포_지도.html')
                    print("전국 급속충전기 분포 지도 생성 완료")
                    
        except Exception as e:
            print(f"지도 생성 오류: {e}")
    
    # 2. 지역별 급속충전기 수 차트
    if charging_df is not None and len(charging_df.columns) > 1:
        try:
            region_col = charging_df.columns[1]
            region_counts = charging_df[region_col].value_counts().head(15)
            
            plt.figure(figsize=(15, 8))
            region_counts.plot(kind='bar')
            plt.title('지역별 급속충전기 수', fontsize=16)
            plt.xlabel('지역', fontsize=12)
            plt.ylabel('급속충전기 수', fontsize=12)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.savefig('results/지역별_급속충전기_수.png', dpi=300, bbox_inches='tight')
            plt.close()
            print("지역별 급속충전기 수 차트 생성 완료")
            
        except Exception as e:
            print(f"차트 생성 오류: {e}")

def main():
    """메인 실행 함수"""
    print("실제 공공데이터포털 데이터 분석 시작")
    
    # 데이터 로드
    charging_df, support_df = load_real_data()
    
    # 급속충전기 데이터 분석
    analyze_charging_data(charging_df)
    
    # 교통약자 이동지원센터 데이터 분석
    analyze_support_data(support_df)
    
    # 시각화 생성
    create_visualizations(charging_df, support_df)
    
    print("\n분석 완료!")

if __name__ == "__main__":
    main() 