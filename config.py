"""
공공데이터포털 API 설정 파일
고등학교 3학년 수준의 탐구를 위한 API 설정
"""

# 공공데이터포털 API 키 설정
# 실제 공공데이터포털에서 발급받은 API 키
PUBLIC_DATA_API_KEY = "xUNNRjnLeRkZsUbQEUswxS7LShDLLr5RZHSducss7RDtPNJNF%2Bqk0EohlM8ERhciUhQIxUfipdrKOuP%2Fl6MUHw%3D%3D"

# API 엔드포인트 설정
API_ENDPOINTS = {
    "charging_station": "https://api.data.go.kr/openapi/tn_pubr_public_electr_whlchairhgh_spdchrgr_api",
    "walkway": "https://api.data.go.kr/openapi/walkway-api", 
    "disability_facilities": "https://api.data.go.kr/openapi/disability-facilities-api"
}

# 대구 지역 설정
DAEGU_REGION = "대구광역시"
DAEGU_DISTRICTS = ['중구', '동구', '서구', '남구', '북구', '수성구', '달서구', '달성군']

# 데이터 수집 설정
DATA_COLLECTION_CONFIG = {
    "page_size": 1000,
    "max_pages": 10,
    "timeout": 30,
    "retry_count": 3
}

# 시각화 설정
VISUALIZATION_CONFIG = {
    "map_center": [35.8714, 128.6014],  # 대구 중심 좌표
    "map_zoom": 12,
    "figure_size": (15, 12),
    "dpi": 300
}

# 색상 설정
COLOR_CONFIG = {
    "walkway_types": {
        "보도블록": "blue",
        "경사로": "green", 
        "엘리베이터": "red",
        "육교": "orange",
        "지하도": "purple"
    },
    "density_levels": {
        "high": "red",      # 80% 이상
        "medium_high": "orange",  # 60-80%
        "medium_low": "yellow",   # 40-60%
        "low": "green"      # 40% 미만
    }
}

def get_api_key():
    """API 키 반환"""
    return PUBLIC_DATA_API_KEY

def is_api_key_set():
    """API 키가 설정되었는지 확인"""
    return PUBLIC_DATA_API_KEY != "YOUR_API_KEY_HERE"

def print_api_setup_instructions():
    """API 설정 안내 출력"""
    print("=" * 60)
    print("공공데이터포털 API 설정 완료!")
    print("=" * 60)
    print("API 키가 설정되었습니다.")
    print("실제 데이터 수집을 시작합니다.")
    print("=" * 60) 