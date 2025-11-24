"""
대화 도메인 모듈
"""
from .model import (
    ConversationCreate,
    ConversationResponse,
    ConversationsListResponse,
    MessageResponse,
    MessagesListResponse,
    ChatRequest,
    MessageRequest,
    ChatResponse
)
from .service import (
    process_chat_message,
    create_conversation,
    get_conversations,
    get_conversation,
    delete_conversation,
    get_messages,
    create_conversation_if_needed
)

__all__ = [
    "ConversationCreate",
    "ConversationResponse",
    "ConversationsListResponse",
    "MessageResponse",
    "MessagesListResponse",
    "ChatRequest",
    "MessageRequest",
    "ChatResponse",
    "process_chat_message",
    "create_conversation",
    "get_conversations",
    "get_conversation",
    "delete_conversation",
    "get_messages",
    "create_conversation_if_needed",
]

