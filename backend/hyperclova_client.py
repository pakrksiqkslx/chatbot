"""
HyperCLOVA X API 클라이언트
"""
import requests
import json
import logging
from typing import List, Dict, Any, Optional
from config import settings

logger = logging.getLogger(__name__)


class HyperCLOVAClient:
    """HyperCLOVA X API 클라이언트"""
    
    # HyperCLOVA X Chat Completions API 엔드포인트
    # v3 API 사용, HCX-005 모델
    HOST = "https://clovastudio.stream.ntruss.com"
    API_ENDPOINT = "/v3/chat-completions/HCX-005"
    
    def __init__(
        self,
        api_key: str = None,
        api_gateway_key: str = None,
        request_id: str = None
    ):
        """
        Args:
            api_key: HyperCLOVA X API 키
            api_gateway_key: API Gateway 키 (선택)
            request_id: 요청 ID (선택)
        """
        self.api_key = api_key or settings.HYPERCLOVA_API_KEY
        self.api_gateway_key = api_gateway_key or settings.HYPERCLOVA_API_GATEWAY_KEY
        self.request_id = request_id or settings.HYPERCLOVA_REQUEST_ID
        
        if not self.api_key:
            raise ValueError("HyperCLOVA API 키가 설정되지 않았습니다")
    
    def _build_headers(self) -> Dict[str, str]:
        """API 요청 헤더 생성 (HyperCLOVA X v3 표준 형식)"""
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json"
        }
        
        # Authorization: Bearer 형식
        if self.api_key.startswith('Bearer '):
            headers["Authorization"] = self.api_key
        else:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        # Request ID (선택적)
        if self.request_id:
            headers["X-NCP-CLOVASTUDIO-REQUEST-ID"] = self.request_id
        
        return headers
    
    def _convert_messages_to_v3_format(self, messages: List[Dict[str, str]]) -> List[Dict]:
        """메시지를 v3 API 형식으로 변환"""
        converted = []
        for msg in messages:
            converted.append({
                "role": msg["role"],
                "content": [
                    {
                        "type": "text",
                        "text": msg["content"]
                    }
                ]
            })
        return converted
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 500,
        temperature: float = 0.5,
        top_k: int = 99,
        top_p: float = 0.8,
        repetition_penalty: float = 1.05,
        stop: List[str] = None,
        seed: int = 0,
        include_ai_filters: bool = True
    ) -> Dict[str, Any]:
        """
        HyperCLOVA X v3 Chat Completions API 호출
        
        Args:
            messages: 대화 메시지 리스트 [{"role": "system|user|assistant", "content": "..."}]
            max_tokens: 최대 생성 토큰 수 (기본값: 500)
            temperature: 생성 토큰 다양성 (0.00~1.00, 기본값: 0.5)
            top_k: Top-K 샘플링 (0~128, 기본값: 99)
            top_p: Top-P 샘플링 (0~1, 기본값: 0.8)
            repetition_penalty: 반복 패널티 (0.0~2.0, 기본값: 1.05)
            stop: 토큰 생성 중단 문자 (기본값: [])
            seed: 결과 일관성 수준 (0~4294967295, 기본값: 0)
            include_ai_filters: AI 필터 포함 여부 (기본값: true)
        
        Returns:
            API 응답 딕셔너리
        """
        try:
            headers = self._build_headers()
            
            # v3 API 형식으로 메시지 변환
            v3_messages = self._convert_messages_to_v3_format(messages)
            
            # HyperCLOVA X v3 API 형식
            payload = {
                "messages": v3_messages,
                "topP": top_p,
                "topK": top_k,
                "maxTokens": max_tokens,
                "temperature": temperature,
                "repetitionPenalty": repetition_penalty,
                "stop": stop if stop else [],
                "seed": seed,
                "includeAiFilters": include_ai_filters
            }
            
            url = self.HOST + self.API_ENDPOINT
            
            logger.info(f"HyperCLOVA X v3 API 호출 중... (메시지 수: {len(messages)})")
            logger.debug(f"URL: {url}")
            logger.debug(f"요청 헤더: {headers}")
            
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            logger.info("HyperCLOVA X API 호출 성공")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"HyperCLOVA X API 호출 실패: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"응답 상태 코드: {e.response.status_code}")
                logger.error(f"응답 내용: {e.response.text}")
            raise
    
    def generate_answer(
        self,
        query: str,
        context_docs: List[Dict[str, Any]],
        system_prompt: str = None
    ) -> str:
        """
        컨텍스트 기반 답변 생성
        
        Args:
            query: 사용자 질문
            context_docs: 검색된 컨텍스트 문서 리스트
            system_prompt: 시스템 프롬프트 (선택)
        
        Returns:
            생성된 답변 텍스트
        """
        # ⚠️ 임시: Mock 응답 사용 (API 키 문제 해결 전까지)
        # TODO: 새로운 CLOVA Studio API 키 발급 후 아래 if 문 제거
        if False:  # Mock 사용 안 함 - 실제 HyperCLOVA X API 호출
            logger.info("Mock 응답 생성 중 (API 키 문제로 임시 사용)")
            return self._generate_mock_answer(query, context_docs)
        
        # 기본 시스템 프롬프트
        if system_prompt is None:
            system_prompt = """당신은 수업계획서 기반 학습 지원 챗봇입니다.
주어진 수업계획서 정보를 바탕으로 학생들의 질문에 정확하고 친절하게 답변해주세요.

답변 시 다음을 지켜주세요:
1. 주어진 컨텍스트 정보를 기반으로만 답변하세요.
2. 확실하지 않은 정보는 추측하지 말고, "제공된 수업계획서에는 해당 정보가 없습니다"라고 답변하세요.
3. 강의명과 교수명을 명확히 언급하세요.
4. 한국어로 자연스럽고 친절하게 답변하세요."""

        # 컨텍스트 구성
        context_text = "\n\n".join([
            f"[관련 정보 {i+1}]\n{doc.get('content', doc.get('page_content', ''))}"
            for i, doc in enumerate(context_docs)
        ])
        
        # 메시지 구성
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"""다음은 수업계획서에서 검색된 관련 정보입니다:

{context_text}

질문: {query}

위 정보를 바탕으로 질문에 답변해주세요."""}
        ]
        
        # API 호출
        response = self.chat(
            messages=messages,
            max_tokens=500,
            temperature=0.5,
            top_p=0.8,
            top_k=99,
            repetition_penalty=1.05
        )
        
        # 답변 추출 (HyperCLOVA X v3 응답 형식)
        # 응답 형식: {"status": {...}, "result": {"message": {"role": "assistant", "content": [{"type": "text", "text": "..."}]}, "usage": {...}}}
        try:
            if "result" in response and "message" in response["result"]:
                message = response["result"]["message"]
                content = message.get("content", [])
                
                # content가 문자열인 경우 (일부 API 버전)
                if isinstance(content, str):
                    return content
                
                # content가 배열인 경우 (v3 표준)
                if isinstance(content, list) and len(content) > 0:
                    first_item = content[0]
                    # 딕셔너리인 경우
                    if isinstance(first_item, dict):
                        return first_item.get("text", "")
                    # 문자열인 경우
                    elif isinstance(first_item, str):
                        return first_item
                
                # 기타 경우
                logger.warning(f"예상치 못한 content 형식: {type(content)}, 값: {content}")
                return str(content) if content else ""
            else:
                logger.error(f"예상치 못한 응답 형식: {response}")
                raise ValueError("API 응답에서 답변을 추출할 수 없습니다")
        except Exception as e:
            logger.error(f"응답 파싱 오류: {e}")
            logger.error(f"전체 응답: {json.dumps(response, ensure_ascii=False, indent=2)}")
            raise
    
    def _generate_mock_answer(self, query: str, context_docs: List[Dict[str, Any]]) -> str:
        """
        Mock 응답 생성 (API 키 문제 해결 전까지 임시 사용)
        FAISS 검색 결과를 바탕으로 간단한 답변 생성
        """
        if not context_docs:
            return "죄송합니다. 관련 정보를 찾을 수 없습니다."
        
        # 가장 유사도가 높은 문서 사용
        top_doc = context_docs[0]
        metadata = top_doc.get('metadata', {})
        content = top_doc.get('content', '')
        
        course_name = metadata.get('course_name', '').strip()
        professor = metadata.get('professor', '').strip()
        section = metadata.get('section', '').strip()
        
        # 질문 유형 파악
        query_lower = query.lower()
        
        # 교수 관련 질문
        if '교수' in query or '선생님' in query or '담당' in query:
            if professor and course_name:
                return f"{course_name}은(는) {professor} 교수님이 담당하고 계십니다.\n\n[검색된 정보]\n{content[:300]}..."
            elif professor:
                return f"{professor} 교수님에 대한 정보를 찾았습니다.\n\n[검색된 정보]\n{content[:300]}..."
        
        # 과목/강의 관련 질문
        if '과목' in query or '강의' in query or '수업' in query:
            if course_name and professor:
                return f"{course_name}에 대한 정보입니다.\n담당교수: {professor} 교수님\n\n[검색된 정보]\n{content[:300]}..."
        
        # 목표 관련 질문
        if '목표' in query or '목적' in query:
            if '수업목표' in content or '교과목개요' in content:
                # 수업목표 부분 추출
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if '수업목표' in line:
                        goal_text = '\n'.join(lines[i:min(i+5, len(lines))])
                        return f"{course_name}의 수업 목표:\n\n{goal_text}"
        
        # 과제 관련 질문
        if '과제' in query or '숙제' in query:
            if section == '과제':
                return f"{course_name}의 과제 정보:\n\n{content[:400]}..."
        
        # 기본 응답
        answer = f"질문하신 '{query}'에 대한 정보를 찾았습니다.\n\n"
        if course_name and professor:
            answer += f"**강의:** {course_name}\n**담당교수:** {professor} 교수님\n**섹션:** {section}\n\n"
        answer += f"[검색된 정보]\n{content[:400]}..."
        
        return answer


# 전역 HyperCLOVA 클라이언트 인스턴스
_hyperclova_client = None


def get_hyperclova_client() -> HyperCLOVAClient:
    """HyperCLOVA 클라이언트 싱글톤 인스턴스 반환"""
    global _hyperclova_client
    if _hyperclova_client is None:
        _hyperclova_client = HyperCLOVAClient()
    return _hyperclova_client

