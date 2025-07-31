"""
교통약자 이동지원센터와 급속충전기 데이터를 활용한 종합 접근성 분석
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

def load_comprehensive_data():
    """두 데이터셋 로드 및 전처리"""
    print("종합 접근성 분석을 위한 데이터 로드 중...")
    
    # 급속충전기 데이터 로드
    charging_df = pd.read_csv('data/전국전동휠체어급속충전기표준데이터.csv', encoding='cp949')
    daegu_charging = charging_df[charging_df['시도명'] == '대구광역시'].copy()
    
    # 교통약자 이동지원센터 데이터 로드
    support_df = pd.read_csv('data/전국교통약자이동지원센터정보표준데이터.csv', encoding='cp949')
    daegu_support = support_df[support_df['소재지도로명주소'].str.contains('대구', na=False)].copy()
    
    print(f"대구 급속충전기: {len(daegu_charging)}개")
    print(f"대구 교통약자 이동지원센터: {len(daegu_support)}개")
    
    return daegu_charging, daegu_support

def calculate_accessibility_score(daegu_charging, daegu_support):
    """구별 장애인휠체어 접근성 점수 계산"""
    print("\n=== 구별 장애인휠체어 접근성 점수 계산 ===")
    
    # 구별 급속충전기 현황
    charging_by_district = daegu_charging['시군구명'].value_counts()
    
    # 구별 교통약자 이동지원센터 현황
    support_by_district = daegu_support['소재지도로명주소'].str.extract(r'대구광역시\s*([^\s]+)')[0].value_counts()
    
    # 모든 구 목록
    all_districts = ['중구', '동구', '서구', '남구', '북구', '수성구', '달서구', '달성군', '군위군']
    
    accessibility_data = []
    
    for district in all_districts:
        # 급속충전기 수
        charging_count = charging_by_district.get(district, 0)
        
        # 교통약자 이동지원센터 수
        support_count = support_by_district.get(district, 0)
        
        # 급속충전기 기능 점수 계산
        district_charging = daegu_charging[daegu_charging['시군구명'] == district]
        
        if len(district_charging) > 0:
            # 24시간 운영 비율
            all_day_ratio = len(district_charging[district_charging['평일운영시작시각'] == '00:00']) / len(district_charging)
            
            # 공기주입가능 비율
            air_pump_ratio = len(district_charging[district_charging['공기주입가능여부'] == 'Y']) / len(district_charging)
            
            # 휴대전화충전가능 비율
            phone_charge_ratio = len(district_charging[district_charging['휴대전화충전가능여부'] == 'Y']) / len(district_charging)
            
            # 평균 동시사용가능대수
            avg_simultaneous = district_charging['동시사용가능대수'].mean()
        else:
            all_day_ratio = 0
            air_pump_ratio = 0
            phone_charge_ratio = 0
            avg_simultaneous = 0
        
        # 종합 접근성 점수 계산 (가중치 적용)
        charging_score = charging_count * 10  # 급속충전기 1개당 10점
        support_score = support_count * 50    # 이동지원센터 1개당 50점
        function_score = (all_day_ratio * 20 + air_pump_ratio * 15 + phone_charge_ratio * 10) * charging_count
        capacity_score = avg_simultaneous * 5 * charging_count
        
        total_score = charging_score + support_score + function_score + capacity_score
        
        accessibility_data.append({
            '구': district,
            '급속충전기_수': charging_count,
            '이동지원센터_수': support_count,
            '24시간운영_비율': all_day_ratio * 100,
            '공기주입가능_비율': air_pump_ratio * 100,
            '휴대전화충전가능_비율': phone_charge_ratio * 100,
            '평균동시사용가능대수': avg_simultaneous,
            '급속충전기_점수': charging_score,
            '이동지원센터_점수': support_score,
            '기능_점수': function_score,
            '용량_점수': capacity_score,
            '종합접근성점수': total_score
        })
    
    accessibility_df = pd.DataFrame(accessibility_data)
    return accessibility_df

def analyze_accessibility_patterns(accessibility_df):
    """접근성 패턴 분석 및 가설 생성"""
    print("\n=== 접근성 패턴 분석 ===")
    
    # 구별 종합 접근성 점수 순위
    accessibility_df_sorted = accessibility_df.sort_values('종합접근성점수', ascending=False)
    
    print("\n구별 종합 접근성 점수 순위:")
    for idx, row in accessibility_df_sorted.iterrows():
        print(f"{row['구']}: {row['종합접근성점수']:.1f}점")
    
    # 접근성 수준 분류
    accessibility_df['접근성수준'] = pd.cut(
        accessibility_df['종합접근성점수'],
        bins=[0, 200, 400, 600, float('inf')],
        labels=['낮음', '보통', '높음', '매우높음']
    )
    
    # 구별 특성 분석
    print("\n=== 구별 특성 분석 ===")
    
    # 급속충전기 밀도가 높은 구
    high_charging = accessibility_df.nlargest(3, '급속충전기_수')
    print("\n급속충전기 밀도 높은 구 (상위 3개):")
    for _, row in high_charging.iterrows():
        print(f"{row['구']}: {row['급속충전기_수']}개")
    
    # 이동지원센터가 있는 구
    has_support = accessibility_df[accessibility_df['이동지원센터_수'] > 0]
    print(f"\n이동지원센터 보유 구: {len(has_support)}개")
    for _, row in has_support.iterrows():
        print(f"{row['구']}: {row['이동지원센터_수']}개")
    
    # 기능이 우수한 구 (24시간 운영 + 공기주입 + 휴대전화충전)
    high_function = accessibility_df[
        (accessibility_df['24시간운영_비율'] > 0) &
        (accessibility_df['공기주입가능_비율'] > 0) &
        (accessibility_df['휴대전화충전가능_비율'] > 0)
    ]
    print(f"\n기능 우수 구: {len(high_function)}개")
    
    return accessibility_df

def generate_hypotheses(accessibility_df):
    """새로운 가설 생성"""
    print("\n=== 새로운 가설 생성 ===")
    
    hypotheses = []
    
    # 가설 1: 도시-농촌 격차 가설
    urban_districts = ['중구', '동구', '서구', '남구', '북구', '수성구', '달서구']
    rural_districts = ['달성군', '군위군']
    
    urban_score = accessibility_df[accessibility_df['구'].isin(urban_districts)]['종합접근성점수'].mean()
    rural_score = accessibility_df[accessibility_df['구'].isin(rural_districts)]['종합접근성점수'].mean()
    
    hypotheses.append({
        '가설명': '도시-농촌 접근성 격차 가설',
        '내용': f'도시 지역({urban_score:.1f}점)의 장애인휠체어 접근성이 농촌 지역({rural_score:.1f}점)보다 높을 것이다.',
        '근거': f'도시 지역 평균 접근성 점수: {urban_score:.1f}점, 농촌 지역: {rural_score:.1f}점',
        '검증방법': '도시-농촌 지역 간 접근성 점수 통계적 비교'
    })
    
    # 가설 2: 이동지원센터 연관성 가설
    with_support = accessibility_df[accessibility_df['이동지원센터_수'] > 0]['종합접근성점수'].mean()
    without_support = accessibility_df[accessibility_df['이동지원센터_수'] == 0]['종합접근성점수'].mean()
    
    hypotheses.append({
        '가설명': '이동지원센터-급속충전기 연관성 가설',
        '내용': f'교통약자 이동지원센터가 있는 지역({with_support:.1f}점)의 급속충전기 접근성이 더 높을 것이다.',
        '근거': f'이동지원센터 보유 지역 평균 점수: {with_support:.1f}점, 미보유 지역: {without_support:.1f}점',
        '검증방법': '이동지원센터 보유 여부에 따른 접근성 점수 비교'
    })
    
    # 가설 3: 기능 통합 가설
    high_function_score = accessibility_df[
        (accessibility_df['24시간운영_비율'] > 0) &
        (accessibility_df['공기주입가능_비율'] > 0) &
        (accessibility_df['휴대전화충전가능_비율'] > 0)
    ]['종합접근성점수'].mean()
    
    low_function_score = accessibility_df[
        ~((accessibility_df['24시간운영_비율'] > 0) &
          (accessibility_df['공기주입가능_비율'] > 0) &
          (accessibility_df['휴대전화충전가능_비율'] > 0))
    ]['종합접근성점수'].mean()
    
    hypotheses.append({
        '가설명': '기능 통합 우수성 가설',
        '내용': '24시간 운영, 공기주입, 휴대전화충전 기능을 모두 갖춘 급속충전기가 많은 지역의 접근성이 더 높을 것이다.',
        '근거': f'기능 통합 지역 평균 점수: {high_function_score:.1f}점, 미통합 지역: {low_function_score:.1f}점',
        '검증방법': '기능 통합도에 따른 접근성 점수 비교'
    })
    
    # 가설 4: 지역 특성 가설
    top_district = accessibility_df.loc[accessibility_df['종합접근성점수'].idxmax()]
    bottom_district = accessibility_df.loc[accessibility_df['종합접근성점수'].idxmin()]
    
    hypotheses.append({
        '가설명': '지역 특성별 접근성 차이 가설',
        '내용': f'지역의 특성(인구밀도, 경제수준, 지리적 위치)에 따라 장애인휠체어 접근성에 차이가 있을 것이다.',
        '근거': f'최고 접근성: {top_district["구"]}({top_district["종합접근성점수"]:.1f}점), 최저: {bottom_district["구"]}({bottom_district["종합접근성점수"]:.1f}점)',
        '검증방법': '지역 특성 변수와 접근성 점수의 상관관계 분석'
    })
    
    return hypotheses

def create_comprehensive_visualizations(accessibility_df, daegu_charging, daegu_support):
    """종합 시각화 생성"""
    print("\n=== 종합 시각화 생성 ===")
    
    # 1. 구별 종합 접근성 점수 차트
    plt.figure(figsize=(12, 8))
    bars = plt.bar(accessibility_df['구'], accessibility_df['종합접근성점수'], 
                   color=['red' if x < 200 else 'orange' if x < 400 else 'yellow' if x < 600 else 'green' 
                          for x in accessibility_df['종합접근성점수']])
    
    plt.title('대구 지역 구별 장애인휠체어 종합 접근성 점수', fontsize=16, fontweight='bold')
    plt.xlabel('구', fontsize=12)
    plt.ylabel('종합 접근성 점수', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', alpha=0.3)
    
    # 값 표시
    for bar, score in zip(bars, accessibility_df['종합접근성점수']):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5, 
                f'{score:.1f}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('results/대구_구별_종합접근성점수.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("구별 종합 접근성 점수 차트 생성 완료")
    
    # 2. 접근성 구성요소 분석 차트
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # 급속충전기 수
    axes[0,0].bar(accessibility_df['구'], accessibility_df['급속충전기_수'], color='skyblue')
    axes[0,0].set_title('구별 급속충전기 수', fontsize=14, fontweight='bold')
    axes[0,0].tick_params(axis='x', rotation=45)
    
    # 이동지원센터 수
    axes[0,1].bar(accessibility_df['구'], accessibility_df['이동지원센터_수'], color='lightgreen')
    axes[0,1].set_title('구별 이동지원센터 수', fontsize=14, fontweight='bold')
    axes[0,1].tick_params(axis='x', rotation=45)
    
    # 24시간 운영 비율
    axes[1,0].bar(accessibility_df['구'], accessibility_df['24시간운영_비율'], color='orange')
    axes[1,0].set_title('구별 24시간 운영 비율 (%)', fontsize=14, fontweight='bold')
    axes[1,0].tick_params(axis='x', rotation=45)
    
    # 평균 동시사용가능대수
    axes[1,1].bar(accessibility_df['구'], accessibility_df['평균동시사용가능대수'], color='purple')
    axes[1,1].set_title('구별 평균 동시사용가능대수', fontsize=14, fontweight='bold')
    axes[1,1].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig('results/대구_접근성_구성요소_분석.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("접근성 구성요소 분석 차트 생성 완료")
    
    # 3. 종합 접근성 지도
    if len(daegu_charging) > 0:
        center_lat = daegu_charging['위도'].mean()
        center_lon = daegu_charging['경도'].mean()
        
        m = folium.Map(location=[center_lat, center_lon], zoom_start=11)
        
        # 구별 색상 매핑 (접근성 점수에 따라)
        colors = ['red', 'orange', 'yellow', 'green']
        accessibility_levels = ['낮음', '보통', '높음', '매우높음']
        
        for idx, row in accessibility_df.iterrows():
            district = row['구']
            score = row['종합접근성점수']
            level = row['접근성수준']
            
            # 접근성 수준에 따른 색상 선택
            color_idx = list(accessibility_levels).index(level) if level in accessibility_levels else 0
            color = colors[color_idx]
            
            # 해당 구의 급속충전기들에 마커 추가
            district_charging = daegu_charging[daegu_charging['시군구명'] == district]
            
            for _, charging_row in district_charging.iterrows():
                popup_text = f"""
                <b>{charging_row['시설명']}</b><br>
                구: {district}<br>
                종합접근성점수: {score:.1f}점<br>
                접근성수준: {level}<br>
                동시사용가능: {charging_row['동시사용가능대수']}대<br>
                공기주입: {charging_row['공기주입가능여부']}<br>
                휴대폰충전: {charging_row['휴대전화충전가능여부']}
                """
                
                folium.Marker(
                    location=[charging_row['위도'], charging_row['경도']],
                    popup=folium.Popup(popup_text, max_width=300),
                    icon=folium.Icon(color=color, icon='info-sign')
                ).add_to(m)
        
        # 범례 추가
        legend_html = '''
        <div style="position: fixed; 
                    top: 10px; right: 10px; width: 200px; height: 120px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <p><b>접근성 수준</b></p>
        '''
        
        for level, color in zip(accessibility_levels, colors):
            legend_html += f'<p><i class="fa fa-map-marker fa-2x" style="color:{color}"></i> {level}</p>'
        
        legend_html += '</div>'
        m.get_root().html.add_child(folium.Element(legend_html))
        
        m.save('results/대구_종합접근성_지도.html')
        print("대구 종합접근성 지도 생성 완료")

def generate_comprehensive_report(accessibility_df, hypotheses):
    """종합 분석 보고서 생성"""
    print("\n=== 종합 분석 보고서 생성 ===")
    
    report = f"""
# 대구 지역 장애인휠체어 종합 접근성 분석 보고서

## 분석 개요
- 분석 대상: 급속충전기 + 교통약자 이동지원센터 통합 데이터
- 분석 기간: {datetime.now().strftime('%Y년 %m월 %d일')}
- 분석 방법: 종합 접근성 점수 산정 및 패턴 분석

## 구별 종합 접근성 점수

"""
    
    # 구별 점수 순위
    accessibility_df_sorted = accessibility_df.sort_values('종합접근성점수', ascending=False)
    for idx, row in accessibility_df_sorted.iterrows():
        report += f"- {row['구']}: {row['종합접근성점수']:.1f}점\n"
    
    report += f"""
## 접근성 구성요소 분석

### 급속충전기 현황
"""
    
    for _, row in accessibility_df.iterrows():
        report += f"- {row['구']}: {row['급속충전기_수']}개 (평균 동시사용가능대수: {row['평균동시사용가능대수']:.1f}대)\n"
    
    report += f"""
### 이동지원센터 현황
"""
    
    for _, row in accessibility_df.iterrows():
        report += f"- {row['구']}: {row['이동지원센터_수']}개\n"
    
    report += f"""
### 기능별 분석
"""
    
    for _, row in accessibility_df.iterrows():
        report += f"- {row['구']}: 24시간운영 {row['24시간운영_비율']:.1f}%, 공기주입 {row['공기주입가능_비율']:.1f}%, 휴대폰충전 {row['휴대전화충전가능_비율']:.1f}%\n"
    
    report += f"""
## 새로운 가설

"""
    
    for i, hypothesis in enumerate(hypotheses, 1):
        report += f"""
### 가설 {i}: {hypothesis['가설명']}
**내용**: {hypothesis['내용']}
**근거**: {hypothesis['근거']}
**검증방법**: {hypothesis['검증방법']}
"""
    
    report += f"""
## 정책 제언

### 1. 접근성 격차 해소
- 군위군, 달성군 등 농촌 지역 급속충전기 확충
- 이동지원센터가 없는 구에 센터 설치 검토

### 2. 기능 개선
- 24시간 운영 시설 비율 향상
- 공기주입 및 휴대전화충전 기능 확대
- 동시사용가능대수 증가

### 3. 통합 서비스
- 급속충전기와 이동지원센터의 연계 강화
- 지역별 맞춤 접근성 향상 방안 수립

## 결론

이번 종합 분석을 통해 대구 지역의 장애인휠체어 접근성을 급속충전기와 이동지원센터 두 가지 관점에서 통합적으로 평가할 수 있었습니다. 특히 구별 접근성 격차와 기능적 차이점을 발견하여, 구체적인 개선 방안과 새로운 연구 가설을 제시할 수 있었습니다.

향후 이러한 종합 접근성 분석 방법론을 다른 지역에도 적용하여 전국적인 장애인 편의시설 개선에 기여할 수 있을 것으로 기대됩니다.
"""
    
    # 보고서 저장
    with open('results/대구_종합접근성_분석보고서.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("대구 종합접근성 분석보고서 생성 완료")
    print(report)

def main():
    """메인 실행 함수"""
    print("대구 지역 종합 접근성 분석 시작")
    
    # 데이터 로드
    daegu_charging, daegu_support = load_comprehensive_data()
    
    # 접근성 점수 계산
    accessibility_df = calculate_accessibility_score(daegu_charging, daegu_support)
    
    # 패턴 분석
    accessibility_df = analyze_accessibility_patterns(accessibility_df)
    
    # 새로운 가설 생성
    hypotheses = generate_hypotheses(accessibility_df)
    
    # 시각화 생성
    create_comprehensive_visualizations(accessibility_df, daegu_charging, daegu_support)
    
    # 보고서 생성
    generate_comprehensive_report(accessibility_df, hypotheses)
    
    print("\n대구 지역 종합 접근성 분석 완료!")

if __name__ == "__main__":
    main() 