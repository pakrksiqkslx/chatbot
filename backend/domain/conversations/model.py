"""
대화 및 메시지 관련 Pydantic 모델
"""
from pydantic import BaseModel
from typing import Optional, List


class ConversationCreate(BaseModel):
    """대화 생성 요청 모델"""
    title: Optional[str] = "새 대화"


class ConversationResponse(BaseModel):
    """대화 응답 모델"""
    id: str
    title: str
    created_at: str
    updated_at: str


class ConversationsListResponse(BaseModel):
    """대화 목록 응답 모델"""
    conversations: List[ConversationResponse]


class MessageResponse(BaseModel):
    """메시지 응답 모델"""
    id: str
    conversation_id: str
    role: str  # "user" or "assistant"
    content: str
    sources: Optional[List[dict]] = []
    order: int
    created_at: str


class MessagesListResponse(BaseModel):
    """메시지 목록 응답 모델"""
    messages: List[MessageResponse]


class ChatRequest(BaseModel):
    """채팅 요청 모델"""
    conversation_id: Optional[str] = None  # None이면 자동으로 새 대화방 생성
    query: str
    k: int = 5
    include_sources: bool = True


class MessageRequest(BaseModel):
    """메시지 추가 요청 모델 (RESTful용)"""
    query: str
    k: int = 5
    include_sources: bool = True


class ChatResponse(BaseModel):
    """채팅 응답 모델"""
    answer: str
    sources: List[dict] = []
    message_id: str

