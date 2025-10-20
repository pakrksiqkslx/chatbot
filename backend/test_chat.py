"""
챗봇 API 테스트 스크립트
"""
import requests
import json

# API 엔드포인트
BASE_URL = "http://localhost:5000"

def test_health():
    """헬스 체크 테스트"""
    print("\n=== 헬스 체크 테스트 ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"상태 코드: {response.status_code}")
    print(f"응답: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.status_code == 200

def test_chat(query: str, k: int = 3):
    """챗봇 테스트"""
    print(f"\n=== 챗봇 테스트: {query} ===")
    
    payload = {
        "query": query,
        "k": k,
        "include_sources": True
    }
    
    response = requests.post(
        f"{BASE_URL}/chat",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"상태 코드: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n[답변]\n{result['answer']}")
        
        if result.get('sources'):
            print(f"\n[출처] ({len(result['sources'])}개 문서)")
            for i, source in enumerate(result['sources'], 1):
                print(f"\n  [{i}] {source['course_name']} - {source['professor']}")
                print(f"      섹션: {source['section']}")
                print(f"      유사도 점수: {source['score']:.4f}")
                print(f"      내용: {source['content_preview'][:150]}...")
    else:
        print(f"오류: {response.text}")
    
    return response.status_code == 200

def main():
    """메인 테스트 함수"""
    print("=" * 60)
    print("수업계획서 챗봇 API 테스트")
    print("=" * 60)
    
    # 1. 헬스 체크
    if not test_health():
        print("\n[X] 헬스 체크 실패! 서버가 실행 중인지 확인하세요.")
        return
    
    print("\n[OK] 헬스 체크 성공!")
    
    # 2. 챗봇 테스트
    test_queries = [
        "C언어프로그래밍 교수님 누구야?",
        "정원석 교수님이 가르치는 과목은?",
        "C언어 수업 목표가 뭐야?",
        "C언어 과제는 어떤 게 있어?",
    ]
    
    success_count = 0
    for query in test_queries:
        if test_chat(query):
            success_count += 1
    
    # 결과 요약
    print("\n" + "=" * 60)
    print(f"테스트 결과: {success_count}/{len(test_queries)} 성공")
    print("=" * 60)

if __name__ == "__main__":
    main()

