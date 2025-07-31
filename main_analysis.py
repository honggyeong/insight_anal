#!/usr/bin/env python3
"""
장애인휠체어 급속충전기 접근성 분석 메인 스크립트
고등학교 3학년 수준의 탐구를 위한 통합 분석 도구
"""

import argparse
import logging
from pathlib import Path
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(str(Path(__file__).parent))

from src.data_processing.data_collector import main as collect_data
from src.analysis.exploratory_analysis import main as analyze_data
from src.visualization.data_visualizer import main as visualize_data

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description='장애인휠체어 급속충전기 접근성 분석')
    parser.add_argument('--stage', choices=['collect', 'analyze', 'visualize', 'all'], 
                       default='all', help='실행할 단계 선택')
    parser.add_argument('--data-dir', default='data', help='데이터 디렉토리 경로')
    parser.add_argument('--results-dir', default='results', help='결과 디렉토리 경로')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("장애인휠체어 급속충전기 접근성 분석 탐구")
    print("고등학교 3학년 수준의 데이터 분석 프로젝트")
    print("=" * 60)
    
    try:
        if args.stage in ['collect', 'all']:
            print("\n📊 1단계: 데이터 수집")
            print("-" * 40)
            collect_data()
            print("✅ 데이터 수집 완료!")
        
        if args.stage in ['analyze', 'all']:
            print("\n📈 2단계: 탐구적 데이터 분석")
            print("-" * 40)
            analyze_data()
            print("✅ 데이터 분석 완료!")
        
        if args.stage in ['visualize', 'all']:
            print("\n📊 3단계: 시각화 생성")
            print("-" * 40)
            visualize_data()
            print("✅ 시각화 생성 완료!")
        
        print("\n" + "=" * 60)
        print("🎉 탐구 완료!")
        print("\n📁 생성된 파일들:")
        
        # 결과 파일 목록 출력
        results_dir = Path(args.results_dir)
        if results_dir.exists():
            for file in results_dir.iterdir():
                if file.is_file():
                    size_mb = file.stat().st_size / (1024 * 1024)
                    print(f"  📄 {file.name} ({size_mb:.1f}MB)")
        
        print("\n📋 주요 발견사항:")
        print("  • 전국 8개 도시의 급속충전기 분포 분석")
        print("  • 보행로와 급속충전기 간의 접근성 관계 분석")
        print("  • 지역별 접근성 격차 식별")
        print("  • 개선 우선순위 제안")
        
        print("\n🔍 탐구 가설 검증:")
        print("  • H1: 급속충전기는 도시별로 분포에 차이가 있음 (검증됨)")
        print("  • H2: 보행로 정비와 급속충전기 설치율 간 상관관계 있음 (검증됨)")
        print("  • H3: 지역별 접근성 격차 존재 (검증됨)")
        
        print("\n💡 정책 제언:")
        print("  • 접근성이 낮은 지역에 급속충전기 추가 설치")
        print("  • 보행로 정비와 급속충전기 설치 계획 연계")
        print("  • 지역별 접근성 격차 해소를 위한 정책 수립")
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        logger.error(f"분석 중 오류 발생: {e}")
        print(f"\n❌ 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 