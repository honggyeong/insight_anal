"""
공공데이터포털 API 대안 URL 테스트
"""

import requests
import json
import config

def test_alternative_urls():
    """다양한 API URL 테스트"""
    print("=" * 60)
    print("공공데이터포털 API 대안 URL 테스트")
    print("=" * 60)
    
    api_key = config.get_api_key()
    
    # 다양한 URL 패턴 테스트
    urls_to_test = [
        "https://api.data.go.kr/openapi/tn_pubr_public_electr_whlchairhgh_spdchrgr_api",
        "https://api.data.go.kr/openapi/tn_pubr_public_electr_whlchairhgh_spdchrgr_api/",
        "https://api.data.go.kr/openapi/tn_pubr_public_electr_whlchairhgh_spdchrgr_api/v1",
        "https://api.data.go.kr/openapi/tn_pubr_public_electr_whlchairhgh_spdchrgr_api/v1/",
        "https://api.data.go.kr/openapi/tn_pubr_public_electr_whlchairhgh_spdchrgr_api/v1/charging-stations",
        "https://api.data.go.kr/openapi/tn_pubr_public_electr_whlchairhgh_spdchrgr_api/charging-stations",
        "https://api.data.go.kr/openapi/tn_pubr_public_electr_whlchairhgh_spdchrgr_api/stations",
        "https://api.data.go.kr/openapi/tn_pubr_public_electr_whlchairhgh_spdchrgr_api/list"
    ]
    
    params = {
        'serviceKey': api_key,
        'pageNo': 1,
        'numOfRows': 10,
        'type': 'json'
    }
    
    for i, url in enumerate(urls_to_test, 1):
        print(f"\n{i}. 테스트 URL: {url}")
        try:
            response = requests.get(url, params=params, timeout=10)
            print(f"   상태 코드: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   성공! 응답 길이: {len(response.text)}")
                data = response.json()
                print(f"   응답 구조: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                break
            else:
                print(f"   실패: {response.status_code}")
                
        except Exception as e:
            print(f"   오류: {str(e)[:100]}...")

def test_with_different_params():
    """다른 파라미터로 테스트"""
    print("\n" + "=" * 60)
    print("다른 파라미터로 API 테스트")
    print("=" * 60)
    
    url = "https://api.data.go.kr/openapi/tn_pubr_public_electr_whlchairhgh_spdchrgr_api"
    api_key = config.get_api_key()
    
    # 다양한 파라미터 조합 테스트
    param_combinations = [
        {'serviceKey': api_key, 'type': 'json'},
        {'serviceKey': api_key, 'type': 'xml'},
        {'serviceKey': api_key, 'pageNo': 1, 'numOfRows': 10},
        {'serviceKey': api_key, 'pageNo': 1, 'numOfRows': 10, 'type': 'json'},
        {'serviceKey': api_key, 'pageNo': 1, 'numOfRows': 10, 'type': 'xml'},
        {'serviceKey': api_key, 'type': 'json', 'dataType': 'JSON'},
        {'serviceKey': api_key, 'type': 'json', 'format': 'json'}
    ]
    
    for i, params in enumerate(param_combinations, 1):
        print(f"\n{i}. 파라미터: {params}")
        try:
            response = requests.get(url, params=params, timeout=10)
            print(f"   상태 코드: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   성공! 응답 길이: {len(response.text)}")
                if 'json' in params.get('type', ''):
                    try:
                        data = response.json()
                        print(f"   JSON 파싱 성공: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                    except:
                        print("   JSON 파싱 실패")
                break
            else:
                print(f"   실패: {response.status_code}")
                
        except Exception as e:
            print(f"   오류: {str(e)[:100]}...")

if __name__ == "__main__":
    test_alternative_urls()
    test_with_different_params() 