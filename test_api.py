"""
공공데이터포털 API 테스트 스크립트
"""

import requests
import json
import config

def test_charging_station_api():
    """장애인휠체어 급속충전기 API 테스트"""
    print("=" * 60)
    print("공공데이터포털 API 테스트")
    print("=" * 60)
    
    url = config.API_ENDPOINTS["charging_station"]
    api_key = config.get_api_key()
    
    print(f"API URL: {url}")
    print(f"API Key: {api_key[:20]}...")
    
    params = {
        'serviceKey': api_key,
        'pageNo': 1,
        'numOfRows': 10,
        'type': 'json'
    }
    
    try:
        print("\nAPI 호출 중...")
        response = requests.get(url, params=params, timeout=30)
        print(f"응답 상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"응답 데이터 구조: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            
            if isinstance(data, dict):
                print(f"응답 내용 (처음 500자): {str(data)[:500]}...")
                
                # 실제 데이터 구조 파악
                if 'response' in data:
                    response_data = data['response']
                    print(f"response 키: {list(response_data.keys())}")
                    
                    if 'body' in response_data:
                        body = response_data['body']
                        print(f"body 키: {list(body.keys())}")
                        
                        if 'items' in body:
                            items = body['items']
                            print(f"items 키: {list(items.keys())}")
                            
                            if 'item' in items:
                                item = items['item']
                                if isinstance(item, list) and len(item) > 0:
                                    print(f"첫 번째 아이템: {item[0]}")
                                else:
                                    print(f"item 내용: {item}")
        else:
            print(f"오류 응답: {response.text}")
            
    except Exception as e:
        print(f"API 호출 실패: {e}")

if __name__ == "__main__":
    test_charging_station_api() 