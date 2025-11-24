"""
대화 관리 API 라우터
"""
from fastapi import APIRouter, HTTPException, Depends, status
import logging

from domain.auth.utils import get_current_user
from domain.conversations.service import (
    process_chat_message,
    create_conversation,
    get_conversations,
    get_conversation,
    delete_conversation,
    get_messages,
    create_conversation_if_needed
)
from domain.conversations.model import (
    ConversationCreate,
    ChatRequest,
    MessageRequest,
    ChatResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"]
)


@router.post(
    "",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="새 대화 생성",
    description="새로운 대화방을 생성합니다."
)
async def create_conversation_endpoint(
    request: ConversationCreate,
    current_user_id: str = Depends(get_current_user)
):
    """
    새 대화 생성

    - **title**: 대화 제목 (기본값: "새 대화")
    """
    try:
        result = await create_conversation(
            user_id=current_user_id,
            title=request.title
        )

        return {
            "success": True,
            "data": {
                "conversation_id": result["conversation_id"],
                "title": result["title"],
                "created_at": result["created_at"].isoformat() + "Z"
            },
            "message": "대화가 생성되었습니다"
        }

    except Exception as e:
        logger.error(f"대화 생성 중 오류 발생: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="대화 생성 중 오류가 발생했습니다"
        )


@router.get(
    "",
    response_model=dict,
    summary="대화 목록 조회",
    description="사용자의 모든 대화를 최신순으로 조회합니다."
)
async def get_conversations_endpoint(
    current_user_id: str = Depends(get_current_user)
):
    """
    내 대화 목록 조회 (최신순)
    """
    try:
        conversations_list = await get_conversations(user_id=current_user_id)

        return {
            "success": True,
            "data": {
                "conversations": conversations_list,
                "total": len(conversations_list)
            }
        }

    except Exception as e:
        logger.error(f"대화 목록 조회 중 오류 발생: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="대화 목록 조회 중 오류가 발생했습니다"
        )


@router.get(
    "/{conversation_id}",
    response_model=dict,
    summary="특정 대화 조회",
    description="특정 대화의 상세 정보를 조회합니다."
)
async def get_conversation_endpoint(
    conversation_id: str,
    current_user_id: str = Depends(get_current_user)
):
    """
    특정 대화 조회
    """
    try:
        conversation = await get_conversation(
            conversation_id=conversation_id,
            user_id=current_user_id
        )

        return {
            "success": True,
            "data": conversation
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"대화 조회 중 오류 발생: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="대화 조회 중 오류가 발생했습니다"
        )


@router.delete(
    "/{conversation_id}",
    response_model=dict,
    summary="대화 삭제",
    description="대화 및 모든 메시지를 삭제합니다."
)
async def delete_conversation_endpoint(
    conversation_id: str,
    current_user_id: str = Depends(get_current_user)
):
    """
    대화 및 모든 메시지 삭제
    """
    try:
        await delete_conversation(
            conversation_id=conversation_id,
            user_id=current_user_id
        )

        return {
            "success": True,
            "message": "대화가 삭제되었습니다"
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"대화 삭제 중 오류 발생: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="대화 삭제 중 오류가 발생했습니다"
        )


@router.get(
    "/{conversation_id}/messages",
    response_model=dict,
    summary="메시지 목록 조회",
    description="특정 대화의 모든 메시지를 순서대로 조회합니다."
)
async def get_messages_endpoint(
    conversation_id: str,
    current_user_id: str = Depends(get_current_user)
):
    """
    대화의 모든 메시지 조회 (순서대로)
    """
    try:
        messages_list = await get_messages(
            conversation_id=conversation_id,
            user_id=current_user_id
        )

        return {
            "success": True,
            "data": {
                "messages": messages_list,
                "total": len(messages_list)
            }
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"메시지 조회 중 오류 발생: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="메시지 조회 중 오류가 발생했습니다"
        )


@router.post(
    "/{conversation_id}/messages",
    response_model=ChatResponse,
    summary="대화방에 메시지 추가 (RESTful)",
    description="특정 대화방에 메시지를 추가하고 AI 응답을 받습니다."
)
async def add_message_to_conversation_endpoint(
    conversation_id: str,
    request: MessageRequest,
    current_user_id: str = Depends(get_current_user)
):
    """
    RESTful 스타일 메시지 추가 API

    Path parameter로 conversation_id를 받습니다.
    """
    try:
        result = await process_chat_message(
            conversation_id=conversation_id,
            query=request.query,
            k=request.k,
            include_sources=request.include_sources,
            current_user_id=current_user_id
        )

        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"],
            message_id=result["message_id"]
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"메시지 추가 중 오류 발생: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
        )


@router.post(
    "/chat",
    response_model=dict,
    summary="채팅하기 (자동 대화방 생성)",
    description="conversation_id가 없으면 자동으로 새 대화방을 생성합니다."
)
async def chat_with_auto_create_endpoint(
    request: ChatRequest,
    current_user_id: str = Depends(get_current_user)
):
    """
    채팅 API (자동 대화방 생성)

    - conversation_id가 없으면 자동으로 새 대화방 생성
    - conversation_id가 있으면 해당 대화방에 메시지 추가
    - 로그인 필수
    """
    try:
        # 필요시 대화 생성
        conversation_id = await create_conversation_if_needed(
            user_id=current_user_id,
            conversation_id=request.conversation_id
        )

        # 메시지 처리
        result = await process_chat_message(
            conversation_id=conversation_id,
            query=request.query,
            k=request.k,
            include_sources=request.include_sources,
            current_user_id=current_user_id
        )

        return {
            "success": True,
            "data": {
                "conversation_id": conversation_id,
                "message_id": result["message_id"],
                "answer": result["answer"],
                "sources": result["sources"]
            }
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"채팅 처리 중 오류 발생: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
        )
