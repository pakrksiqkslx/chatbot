"""
대화 관련 비즈니스 로직 서비스
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional
from bson import ObjectId
from bson.errors import InvalidId

from infrastructure.database import Collections, db_instance
from domain.chat.client import get_hyperclova_client
from domain.chat.vectorstore import get_vectorstore_service
from domain.chat.title import auto_generate_title

logger = logging.getLogger(__name__)


async def process_chat_message(
    conversation_id: str,
    query: str,
    k: int,
    include_sources: bool,
    current_user_id: str
) -> Dict:
    """
    채팅 메시지 처리 비즈니스 로직

    Args:
        conversation_id: 대화 ID
        query: 사용자 질문
        k: 검색 결과 수
        include_sources: 출처 포함 여부
        current_user_id: 현재 사용자 ID

    Returns:
        {"answer": str, "sources": list, "message_id": str, "conversation_id": str}

    Raises:
        ValueError: 유효하지 않은 대화 ID
        PermissionError: 대화 소유권 없음
    """
    conversations_collection = db_instance.get_collection(Collections.CONVERSATIONS)
    messages_collection = db_instance.get_collection(Collections.MESSAGES)

    # ObjectId 변환
    try:
        conv_object_id = ObjectId(conversation_id)
    except (InvalidId, TypeError):
        raise ValueError("유효하지 않은 대화 ID입니다")

    # 1. 대화방 확인 및 소유권 검증
    conversation = await conversations_collection.find_one({
        "_id": conv_object_id,
        "user_id": ObjectId(current_user_id)
    })

    if not conversation:
        raise PermissionError("대화를 찾을 수 없거나 접근 권한이 없습니다")

    logger.info(f"채팅 요청: {query} (대화: {conversation_id})")

    # 2. 최근 메시지 3개 조회 (대화 흐름 유지용)
    recent_messages = await messages_collection.find(
        {"conversation_id": conv_object_id}
    ).sort("order", -1).limit(3).to_list(length=3)
    
    # 최근 메시지를 시간순으로 정렬 (오래된 것부터)
    recent_messages.reverse()
    
    # 메시지 히스토리 구성 (role과 content만)
    message_history = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in recent_messages
    ]
    
    logger.info(f"최근 메시지 {len(message_history)}개를 컨텍스트로 포함")

    # 3. 현재 메시지 순서 계산
    message_count = await messages_collection.count_documents(
        {"conversation_id": conv_object_id}
    )
    user_message_order = message_count
    bot_message_order = message_count + 1

    # 4. 사용자 메시지 저장
    now = datetime.utcnow()
    user_message_doc = {
        "conversation_id": conv_object_id,
        "role": "user",
        "content": query,
        "order": user_message_order,
        "created_at": now
    }
    await messages_collection.insert_one(user_message_doc)

    # 5. AI 응답 생성
    hyperclova = get_hyperclova_client()

    # 5-1. 질문 의도 분류
    intent = await hyperclova.classify_intent(query)
    logger.info(f"질문 의도: {intent}")

    # 5-2. 일상 대화인 경우 바로 답변
    if intent == 'casual_chat':
        logger.info("일상 대화로 분류 - 직접 답변 생성")
        answer = await hyperclova.generate_casual_answer(query, message_history)
        sources = []
    else:
        # 5-3. 수업 관련: Pinecone 벡터 검색
        logger.info(f"{intent} 분류 - 벡터 검색 수행")

        vectorstore = get_vectorstore_service()
        search_results = await vectorstore.similarity_search(
            query=query,
            k=k
        )

        if not search_results:
            answer = "죄송합니다. 관련 수업 정보를 찾을 수 없습니다. 다른 방식으로 질문해주시겠어요?"
            sources = []
        else:
            logger.info(f"검색된 문서 수: {len(search_results)}")

            # 5-4. HyperCLOVA 답변 생성 (최근 메시지 히스토리 포함)
            answer = await hyperclova.generate_answer(
                query=query,
                context_docs=search_results,
                message_history=message_history
            )

            # 5-5. 출처 구성
            sources = []
            if include_sources:
                for result in search_results:
                    sources.append({
                        "course_name": result["metadata"].get("course_name", ""),
                        "professor": result["metadata"].get("professor", ""),
                        "section": result["metadata"].get("section", ""),
                        "content_preview": result["page_content"][:200] + "..."
                    })

    # 6. 봇 메시지 저장
    bot_message_doc = {
        "conversation_id": conv_object_id,
        "role": "assistant",
        "content": answer,
        "sources": sources,
        "order": bot_message_order,
        "created_at": datetime.utcnow()
    }
    bot_message_result = await messages_collection.insert_one(bot_message_doc)
    bot_message_id = str(bot_message_result.inserted_id)

    # 7. 대화방 updated_at 갱신
    await conversations_collection.update_one(
        {"_id": conv_object_id},
        {"$set": {"updated_at": datetime.utcnow()}}
    )

    # 8. 자동 제목 생성 (1번째 또는 5번째 대화)
    new_message_count = bot_message_order + 1  # 사용자 + 봇 메시지 포함
    if new_message_count == 2 or new_message_count == 10:
        await auto_generate_title(
            conversation_id=conversation_id,
            message_count=new_message_count,
            user_query=query
        )

    logger.info("답변 생성 완료")

    return {
        "answer": answer,
        "sources": sources,
        "message_id": bot_message_id,
        "conversation_id": conversation_id
    }


async def create_conversation(user_id: str, title: str = "새 대화") -> Dict:
    """
    새 대화 생성

    Args:
        user_id: 사용자 ID
        title: 대화 제목

    Returns:
        {"conversation_id": str, "title": str, "created_at": datetime}
    """
    conversations_collection = db_instance.get_collection(Collections.CONVERSATIONS)

    now = datetime.utcnow()
    conversation_doc = {
        "user_id": ObjectId(user_id),
        "title": title,
        "created_at": now,
        "updated_at": now
    }

    result = await conversations_collection.insert_one(conversation_doc)
    conversation_id = str(result.inserted_id)

    logger.info(f"새 대화 생성: {conversation_id} (사용자: {user_id})")

    return {
        "conversation_id": conversation_id,
        "title": title,
        "created_at": now
    }


async def get_conversations(user_id: str) -> List[Dict]:
    """
    사용자의 대화 목록 조회

    Args:
        user_id: 사용자 ID

    Returns:
        대화 목록 리스트
    """
    conversations_collection = db_instance.get_collection(Collections.CONVERSATIONS)

    conversations = await conversations_collection.find(
        {"user_id": ObjectId(user_id)}
    ).sort("updated_at", -1).to_list(length=100)

    conversations_list = [
        {
            "id": str(conv["_id"]),
            "title": conv["title"],
            "created_at": conv["created_at"].isoformat() + "Z",
            "updated_at": conv["updated_at"].isoformat() + "Z"
        }
        for conv in conversations
    ]

    logger.info(f"대화 목록 조회: {len(conversations_list)}개 (사용자: {user_id})")

    return conversations_list


async def get_conversation(conversation_id: str, user_id: str) -> Dict:
    """
    특정 대화 조회

    Args:
        conversation_id: 대화 ID
        user_id: 사용자 ID

    Returns:
        대화 정보 딕셔너리

    Raises:
        ValueError: 유효하지 않은 대화 ID
        PermissionError: 대화 소유권 없음
    """
    conversations_collection = db_instance.get_collection(Collections.CONVERSATIONS)

    # ObjectId 변환
    try:
        conv_object_id = ObjectId(conversation_id)
    except (InvalidId, TypeError):
        raise ValueError("유효하지 않은 대화 ID입니다")

    conversation = await conversations_collection.find_one({
        "_id": conv_object_id,
        "user_id": ObjectId(user_id)
    })

    if not conversation:
        raise PermissionError("대화를 찾을 수 없거나 접근 권한이 없습니다")

    return {
        "id": str(conversation["_id"]),
        "title": conversation["title"],
        "created_at": conversation["created_at"].isoformat() + "Z",
        "updated_at": conversation["updated_at"].isoformat() + "Z"
    }


async def delete_conversation(conversation_id: str, user_id: str) -> None:
    """
    대화 및 모든 메시지 삭제

    Args:
        conversation_id: 대화 ID
        user_id: 사용자 ID

    Raises:
        ValueError: 유효하지 않은 대화 ID
        PermissionError: 대화 소유권 없음
    """
    conversations_collection = db_instance.get_collection(Collections.CONVERSATIONS)
    messages_collection = db_instance.get_collection(Collections.MESSAGES)

    # ObjectId 변환
    try:
        conv_object_id = ObjectId(conversation_id)
    except (InvalidId, TypeError):
        raise ValueError("유효하지 않은 대화 ID입니다")

    # 소유권 확인
    conversation = await conversations_collection.find_one({
        "_id": conv_object_id,
        "user_id": ObjectId(user_id)
    })

    if not conversation:
        raise PermissionError("대화를 찾을 수 없거나 접근 권한이 없습니다")

    # 메시지 삭제
    await messages_collection.delete_many({"conversation_id": conv_object_id})

    # 대화 삭제
    await conversations_collection.delete_one({"_id": conv_object_id})

    logger.info(f"대화 삭제: {conversation_id} (사용자: {user_id})")


async def get_messages(conversation_id: str, user_id: str) -> List[Dict]:
    """
    대화의 모든 메시지 조회

    Args:
        conversation_id: 대화 ID
        user_id: 사용자 ID

    Returns:
        메시지 목록 리스트

    Raises:
        ValueError: 유효하지 않은 대화 ID
        PermissionError: 대화 소유권 없음
    """
    conversations_collection = db_instance.get_collection(Collections.CONVERSATIONS)
    messages_collection = db_instance.get_collection(Collections.MESSAGES)

    # ObjectId 변환
    try:
        conv_object_id = ObjectId(conversation_id)
    except (InvalidId, TypeError):
        raise ValueError("유효하지 않은 대화 ID입니다")

    # 소유권 확인
    conversation = await conversations_collection.find_one({
        "_id": conv_object_id,
        "user_id": ObjectId(user_id)
    })

    if not conversation:
        raise PermissionError("대화를 찾을 수 없거나 접근 권한이 없습니다")

    # 메시지 조회
    messages = await messages_collection.find(
        {"conversation_id": conv_object_id}
    ).sort("order", 1).to_list(length=1000)

    messages_list = [
        {
            "id": str(msg["_id"]),
            "conversation_id": conversation_id,
            "role": msg["role"],
            "content": msg["content"],
            "sources": msg.get("sources", []),
            "order": msg["order"],
            "created_at": msg["created_at"].isoformat() + "Z"
        }
        for msg in messages
    ]

    logger.info(f"메시지 목록 조회: {len(messages_list)}개 (대화: {conversation_id})")

    return messages_list


async def create_conversation_if_needed(user_id: str, conversation_id: Optional[str] = None) -> str:
    """
    필요시 대화 생성 (없으면 생성, 있으면 반환)

    Args:
        user_id: 사용자 ID
        conversation_id: 기존 대화 ID (None이면 새로 생성)

    Returns:
        대화 ID
    """
    if conversation_id:
        return conversation_id

    logger.info(f"새 대화방 자동 생성 (사용자: {user_id})")

    result = await create_conversation(user_id, "새 대화")
    conversation_id = result["conversation_id"]

    logger.info(f"새 대화방 생성 완료: {conversation_id}")

    return conversation_id

