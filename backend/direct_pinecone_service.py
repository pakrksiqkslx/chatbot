"""
백엔드용 PINECONE 벡터 스토어 서비스 (비동기 버전)
LangChain 호환성 문제를 우회하여 PINECONE API v5를 직접 사용
"""

import os
import logging
import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# HuggingFace 임베딩 모델 사용 (한국어 특화)
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings

# PINECONE API v5 사용 (동기 클라이언트를 비동기로 래핑)
from pinecone import Pinecone
import json

from config import settings

logger = logging.getLogger(__name__)


class DirectPineconeVectorStoreService:
    """PINECONE API 직접 사용 벡터 스토어 서비스 (비동기)"""
    
    def __init__(self):
        """서비스 초기화"""
        self.embeddings = None
        self.pc = None
        self.index = None
        self._executor = ThreadPoolExecutor(max_workers=4)  # I/O 및 CPU 바운드 작업을 위한 스레드 풀
        self._initialize()
    
    def _initialize(self):
        """벡터 스토어 초기화"""
        try:
            # 임베딩 모델 초기화
            self.embeddings = HuggingFaceEmbeddings(
                model_name="jhgan/ko-sroberta-multitask",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            logger.info("임베딩 모델 초기화 완료")
            
            # PINECONE 클라이언트 초기화
            if settings.PINECONE_API_KEY:
                self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
                self.index = self.pc.Index(settings.PINECONE_INDEX_NAME)
                logger.info(f"PINECONE 벡터 스토어 로딩 완료: {settings.PINECONE_INDEX_NAME}")
            else:
                logger.error("PINECONE API 키가 설정되지 않았습니다.")
                raise ValueError("PINECONE_API_KEY가 필요합니다.")
                
        except Exception as e:
            logger.error(f"벡터 스토어 초기화 실패: {e}")
            raise
    
    async def _embed_query_async(self, query: str) -> List[float]:
        """임베딩 생성 (CPU 바운드 작업을 스레드 풀에서 실행)"""
        loop = asyncio.get_event_loop()
        embedding = await loop.run_in_executor(
            self._executor,
            self.embeddings.embed_query,
            query
        )
        return embedding
    
    def _query_pinecone(self, query_embedding: List[float], k: int):
        """Pinecone 쿼리 헬퍼 메서드 (스레드 풀에서 실행)"""
        return self.index.query(
            vector=query_embedding,
            top_k=k,
            include_metadata=True
        )
    
    async def similarity_search(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        """
        유사도 검색 수행 (비동기)
        
        Args:
            query: 검색 쿼리
            k: 반환할 결과 수
            
        Returns:
            검색 결과 리스트
        """
        try:
            if not self.index:
                raise ValueError("PINECONE이 초기화되지 않았습니다.")
            
            # 쿼리를 벡터로 변환 (비동기 - 스레드 풀 사용)
            query_embedding = await self._embed_query_async(query)
            
            # PINECONE에서 비동기 검색 (동기 호출을 스레드 풀에서 실행)
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                self._executor,
                self._query_pinecone,
                query_embedding,
                k
            )
            
            # 결과를 LangChain 형식으로 변환
            documents = []
            for match in results.matches:
                # 실제 본문 텍스트 반환
                doc = {
                    "page_content": match.metadata.get("text", ""),  # 실제 본문
                    "metadata": match.metadata
                }
                documents.append(doc)
            
            logger.info(f"검색 완료: {len(documents)}개 결과")
            return documents
            
        except Exception as e:
            logger.error(f"검색 실패: {e}")
            return []
    
    async def get_relevant_documents(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        """LangChain 호환 메서드 (비동기)"""
        return await self.similarity_search(query, k)


# 싱글톤 인스턴스
_vectorstore_service = None


def get_vectorstore_service() -> DirectPineconeVectorStoreService:
    """벡터 스토어 서비스 싱글톤 인스턴스 반환"""
    global _vectorstore_service
    if _vectorstore_service is None:
        _vectorstore_service = DirectPineconeVectorStoreService()
    return _vectorstore_service
