"""
실제 데이터를 사용한 대구 지역 장애인휠체어 급속충전기 분석
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

def load_daegu_data():
    """대구 지역 데이터 로드 및 필터링"""
    print("대구 지역 데이터 로드 중...")
    
    # 급속충전기 데이터 로드
    charging_df = pd.read_csv('data/전국전동휠체어급속충전기표준데이터.csv', encoding='cp949')
    
    # 대구 지역만 필터링
    daegu_charging = charging_df[charging_df['시도명'] == '대구광역시'].copy()
    
    print(f"대구 지역 급속충전기 수: {len(daegu_charging)}")
    
    # 교통약자 이동지원센터 데이터 로드
    try:
        support_df = pd.read_csv('data/전국교통약자이동지원센터정보표준데이터.csv', encoding='cp949')
        # 대구 지역 센터 필터링 (주소에 '대구' 포함)
        daegu_support = support_df[support_df['소재지도로명주소'].str.contains('대구', na=False)].copy()
        print(f"대구 지역 교통약자 이동지원센터 수: {len(daegu_support)}")
    except:
        daegu_support = None
        print("교통약자 이동지원센터 데이터 로드 실패")
    
    return daegu_charging, daegu_support

def analyze_daegu_charging(daegu_charging):
    """대구 지역 급속충전기 상세 분석"""
    print("\n=== 대구 지역 급속충전기 상세 분석 ===")
    
    # 구별 분포
    district_counts = daegu_charging['시군구명'].value_counts()
    print("\n구별 급속충전기 분포:")
    for district, count in district_counts.items():
        print(f"{district}: {count}개")
    
    # 동시사용가능대수 분석
    print(f"\n동시사용가능대수 통계:")
    print(f"평균: {daegu_charging['동시사용가능대수'].mean():.1f}")
    print(f"최대: {daegu_charging['동시사용가능대수'].max()}")
    print(f"최소: {daegu_charging['동시사용가능대수'].min()}")
    
    # 운영시간 분석
    print(f"\n운영시간 분석:")
    print(f"24시간 운영: {len(daegu_charging[daegu_charging['평일운영시작시각'] == '00:00'])}개")
    print(f"평일 운영: {len(daegu_charging[daegu_charging['평일운영시작시각'] != '00:00'])}개")
    
    # 공기주입가능여부
    air_pump_counts = daegu_charging['공기주입가능여부'].value_counts()
    print(f"\n공기주입가능여부:")
    for status, count in air_pump_counts.items():
        print(f"{status}: {count}개")
    
    # 휴대전화충전가능여부
    phone_charge_counts = daegu_charging['휴대전화충전가능여부'].value_counts()
    print(f"\n휴대전화충전가능여부:")
    for status, count in phone_charge_counts.items():
        print(f"{status}: {count}개")
    
    return district_counts

def analyze_daegu_support(daegu_support):
    """대구 지역 교통약자 이동지원센터 분석"""
    if daegu_support is None or len(daegu_support) == 0:
        print("\n대구 지역 교통약자 이동지원센터 데이터가 없습니다.")
        return
    
    print("\n=== 대구 지역 교통약자 이동지원센터 분석 ===")
    
    print(f"총 센터 수: {len(daegu_support)}")
    
    # 보유차량대수 분석
    if '보유차량대수' in daegu_support.columns:
        vehicle_counts = daegu_support['보유차량대수'].value_counts()
        print(f"\n보유차량대수 분포:")
        for count, num in vehicle_counts.items():
            print(f"{count}대: {num}개 센터")
    
    # 슬로프형/리프트형 차량 분석
    if '슬로프형휠체어차량대수' in daegu_support.columns:
        slope_vehicles = daegu_support['슬로프형휠체어차량대수'].sum()
        print(f"\n슬로프형휠체어차량 총 대수: {slope_vehicles}대")
    
    if '리프트형휠체어차량대수' in daegu_support.columns:
        lift_vehicles = daegu_support['리프트형휠체어차량대수'].sum()
        print(f"리프트형휠체어차량 총 대수: {lift_vehicles}대")

def create_daegu_visualizations(daegu_charging, daegu_support, district_counts):
    """대구 지역 시각화 생성"""
    print("\n=== 대구 지역 시각화 생성 ===")
    
    # 1. 대구 급속충전기 분포 지도
    if len(daegu_charging) > 0:
        # 대구 중심 좌표
        center_lat = daegu_charging['위도'].mean()
        center_lon = daegu_charging['경도'].mean()
        
        m = folium.Map(location=[center_lat, center_lon], zoom_start=11)
        
        # 구별 색상 매핑
        colors = ['red', 'blue', 'green', 'orange', 'purple', 'darkred', 'lightred', 'beige']
        district_colors = {}
        
        for i, district in enumerate(district_counts.index):
            district_colors[district] = colors[i % len(colors)]
        
        # 급속충전기 마커 추가
        for idx, row in daegu_charging.iterrows():
            color = district_colors.get(row['시군구명'], 'gray')
            
            popup_text = f"""
            <b>{row['시설명']}</b><br>
            구: {row['시군구명']}<br>
            주소: {row['소재지도로명주소']}<br>
            동시사용가능: {row['동시사용가능대수']}대<br>
            공기주입: {row['공기주입가능여부']}<br>
            휴대폰충전: {row['휴대전화충전가능여부']}
            """
            
            folium.Marker(
                location=[row['위도'], row['경도']],
                popup=folium.Popup(popup_text, max_width=300),
                icon=folium.Icon(color=color, icon='info-sign')
            ).add_to(m)
        
        # 범례 추가
        legend_html = '''
        <div style="position: fixed; 
                    top: 10px; right: 10px; width: 150px; height: 90px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <p><b>구별 급속충전기</b></p>
        '''
        
        for district, color in district_colors.items():
            legend_html += f'<p><i class="fa fa-map-marker fa-2x" style="color:{color}"></i> {district}</p>'
        
        legend_html += '</div>'
        m.get_root().html.add_child(folium.Element(legend_html))
        
        m.save('results/대구_급속충전기_실제분포_지도.html')
        print("대구 급속충전기 실제분포 지도 생성 완료")
    
    # 2. 구별 급속충전기 수 차트
    plt.figure(figsize=(12, 8))
    district_counts.plot(kind='bar', color='skyblue', edgecolor='black')
    plt.title('대구 지역 구별 급속충전기 수', fontsize=16, fontweight='bold')
    plt.xlabel('구', fontsize=12)
    plt.ylabel('급속충전기 수', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', alpha=0.3)
    
    # 값 표시
    for i, v in enumerate(district_counts.values):
        plt.text(i, v + 0.5, str(v), ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('results/대구_구별_급속충전기_수.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("대구 구별 급속충전기 수 차트 생성 완료")
    
    # 3. 동시사용가능대수 분포 차트
    plt.figure(figsize=(10, 6))
    daegu_charging['동시사용가능대수'].value_counts().sort_index().plot(kind='bar', color='lightgreen')
    plt.title('대구 지역 동시사용가능대수 분포', fontsize=16, fontweight='bold')
    plt.xlabel('동시사용가능대수', fontsize=12)
    plt.ylabel('급속충전기 수', fontsize=12)
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig('results/대구_동시사용가능대수_분포.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("대구 동시사용가능대수 분포 차트 생성 완료")
    
    # 4. 기능별 분석 차트
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    
    # 공기주입가능여부
    air_pump_counts = daegu_charging['공기주입가능여부'].value_counts()
    axes[0].pie(air_pump_counts.values, labels=air_pump_counts.index, autopct='%1.1f%%', startangle=90)
    axes[0].set_title('공기주입가능여부', fontsize=14, fontweight='bold')
    
    # 휴대전화충전가능여부
    phone_charge_counts = daegu_charging['휴대전화충전가능여부'].value_counts()
    axes[1].pie(phone_charge_counts.values, labels=phone_charge_counts.index, autopct='%1.1f%%', startangle=90)
    axes[1].set_title('휴대전화충전가능여부', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('results/대구_기능별_분석.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("대구 기능별 분석 차트 생성 완료")

def generate_daegu_report(daegu_charging, daegu_support, district_counts):
    """대구 지역 분석 보고서 생성"""
    print("\n=== 대구 지역 분석 보고서 ===")
    
    report = f"""
# 대구 지역 장애인휠체어 급속충전기 실제 데이터 분석 보고서

## 분석 개요
- 분석 대상: 전국전동휠체어급속충전기표준데이터 (대구 지역)
- 분석 기간: {datetime.now().strftime('%Y년 %m월 %d일')}
- 총 급속충전기 수: {len(daegu_charging)}개

## 구별 분포 현황
"""
    
    for district, count in district_counts.items():
        percentage = (count / len(daegu_charging)) * 100
        report += f"- {district}: {count}개 ({percentage:.1f}%)\n"
    
    # 평균 동시사용가능대수
    avg_simultaneous = daegu_charging['동시사용가능대수'].mean()
    report += f"\n## 시설 현황\n"
    report += f"- 평균 동시사용가능대수: {avg_simultaneous:.1f}대\n"
    
    # 24시간 운영 시설
    all_day_count = len(daegu_charging[daegu_charging['평일운영시작시각'] == '00:00'])
    report += f"- 24시간 운영 시설: {all_day_count}개\n"
    
    # 공기주입가능 시설
    air_pump_count = len(daegu_charging[daegu_charging['공기주입가능여부'] == 'Y'])
    report += f"- 공기주입가능 시설: {air_pump_count}개\n"
    
    # 휴대전화충전가능 시설
    phone_charge_count = len(daegu_charging[daegu_charging['휴대전화충전가능여부'] == 'Y'])
    report += f"- 휴대전화충전가능 시설: {phone_charge_count}개\n"
    
    if daegu_support is not None and len(daegu_support) > 0:
        report += f"\n## 교통약자 이동지원센터 현황\n"
        report += f"- 총 센터 수: {len(daegu_support)}개\n"
        
        if '보유차량대수' in daegu_support.columns:
            total_vehicles = daegu_support['보유차량대수'].sum()
            report += f"- 총 보유차량대수: {total_vehicles}대\n"
    
    report += f"\n## 주요 발견사항\n"
    
    # 가장 많은 급속충전기가 있는 구
    max_district = district_counts.index[0]
    max_count = district_counts.iloc[0]
    report += f"- 가장 많은 급속충전기: {max_district} ({max_count}개)\n"
    
    # 가장 적은 급속충전기가 있는 구
    min_district = district_counts.index[-1]
    min_count = district_counts.iloc[-1]
    report += f"- 가장 적은 급속충전기: {min_district} ({min_count}개)\n"
    
    # 격차 분석
    gap = max_count - min_count
    report += f"- 구별 격차: {gap}개\n"
    
    report += f"\n## 정책 제언\n"
    report += f"1. {min_district} 지역 급속충전기 확충 필요\n"
    report += f"2. 24시간 운영 시설 비율 향상 필요\n"
    report += f"3. 공기주입 및 휴대전화충전 기능 확대\n"
    
    # 보고서 저장
    with open('results/대구_실제데이터_분석보고서.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("대구 실제데이터 분석보고서 생성 완료")
    print(report)

def main():
    """메인 실행 함수"""
    print("대구 지역 실제 데이터 분석 시작")
    
    # 데이터 로드
    daegu_charging, daegu_support = load_daegu_data()
    
    # 급속충전기 분석
    district_counts = analyze_daegu_charging(daegu_charging)
    
    # 교통약자 이동지원센터 분석
    analyze_daegu_support(daegu_support)
    
    # 시각화 생성
    create_daegu_visualizations(daegu_charging, daegu_support, district_counts)
    
    # 보고서 생성
    generate_daegu_report(daegu_charging, daegu_support, district_counts)
    
    print("\n대구 지역 실제 데이터 분석 완료!")

if __name__ == "__main__":
    main() 