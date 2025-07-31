# 대구 지역 장애인휠체어 급속충전기 접근성 분석 탐구

## 탐구 주제
**"공공데이터포털을 활용한 대구 지역 장애인휠체어 급속충전기와 보행로 접근성 분석"**

## 탐구 목표
- 공공데이터포털에서 실제 데이터 수집
- 대구 지역 보행로와 급속충전기 분포 시각화
- 지역별 접근성 격차 분석 및 개선 방안 제시

## 탐구 가설
1. **H1**: 대구 지역 내에서도 구별로 급속충전기 분포에 차이가 있을 것이다
2. **H2**: 보행로가 잘 정비된 구일수록 급속충전기 접근성이 높을 것이다
3. **H3**: 구별로 휠체어 접근성에 차이가 있을 것이다

## 공공데이터포털 API 사용 방법

### 1. API 키 발급
1. [공공데이터포털](https://www.data.go.kr/) 접속
2. 회원가입 및 로그인
3. "전국 장애인휠체어 급속충전기 설치현황" 검색
4. API 신청 및 승인 대기
5. 승인 후 API 키 발급

### 2. 사용 가능한 API 목록
- **전국 장애인휠체어 급속충전기 설치현황**
  - URL: `http://api.data.go.kr/openapi/charging-station-api`
  - 대구 지역 필터링 가능
  
- **보행로 정비 현황**
  - URL: `http://api.data.go.kr/openapi/walkway-api`
  - 대구 지역 보행로 정보
  
- **장애인 편의시설 설치현황**
  - URL: `http://api.data.go.kr/openapi/disability-facilities-api`
  - 대구 지역 편의시설 정보

### 3. API 키 설정
```python
# src/data_processing/data_collector.py 파일에서
class PublicDataPortalCollector:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or "YOUR_ACTUAL_API_KEY"  # 여기에 실제 API 키 입력
```

### 4. 데이터 수집 실행
```bash
python3 src/data_processing/data_collector.py
```

## 데이터 소스
1. **공공데이터포털**: 전국 장애인휠체어 급속충전기 설치현황
2. **공공데이터포털**: 보행로 정비 현황
3. **공공데이터포털**: 장애인 편의시설 설치현황

## 분석 방법
### 1. 탐색적 데이터 분석 (EDA)
- 대구 지역 급속충전기 분포 시각화
- 보행로와 급속충전기 간의 접근성 관계 분석
- 구별 접근성 지수 계산 및 지도 시각화

### 2. 통계 분석
- 구별 급속충전기 밀도 비교 (t-검정)
- 보행로 정비율과 급속충전기 설치율 상관분석
- 접근성 격차 분석

### 3. 시각화
- 대구 지도상 급속충전기 분포도 (색상으로 밀도 표시)
- 보행로 지도 (타입별, 접근성별 구분)
- 구별 접근성 히트맵
- 보행로-급속충전기 거리 분석 그래프

## 프로젝트 구조
```
insight/
├── data/                    # 데이터 파일
├── notebooks/              # Jupyter 노트북
├── src/
│   ├── data_processing/    # 공공데이터포털 데이터 수집
│   ├── analysis/          # 탐구 분석
│   ├── visualization/     # 시각화
│   └── models/           # 예측 모델
├── results/               # 분석 결과
└── docs/                 # 문서
```

## 탐구 도구
- **Python**: 데이터 분석 및 시각화
- **Pandas**: 데이터 처리
- **Matplotlib/Seaborn**: 그래프 작성
- **Folium**: 지도 시각화
- **Requests**: 공공데이터포털 API 호출
- **Scikit-learn**: 통계 분석

## 기대 결과
1. 대구 지역 급속충전기 접근성 현황 파악
2. 접근성이 부족한 구 식별
3. 개선 우선순위 제안
4. 정책 제언서 작성

## 실행 방법

### 1. API 키 설정 후 데이터 수집
```bash
# API 키를 설정한 후
python3 src/data_processing/data_collector.py
```

### 2. 시각화 생성
```bash
python3 src/visualization/data_visualizer.py
```

### 3. 전체 분석 실행
```bash
python3 main_analysis.py
```

## 생성되는 결과물
- `daegu_walkway_map.html`: 대구 보행로 지도
- `daegu_charging_distribution_map.html`: 급속충전기 분포 지도 (색상으로 밀도 표시)
- `daegu_combined_map.html`: 보행로와 급속충전기 통합 지도
- `daegu_district_analysis.png`: 구별 분석 차트 