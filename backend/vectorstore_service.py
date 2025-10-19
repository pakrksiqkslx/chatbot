"""
FAISS 벡터 스토어 검색 서비스
"""
import os
from typing import List, Dict, Any
from pathlib import Path
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from config import settings
import logging

logger = logging.getLogger(__name__)


class VectorStoreService:
    """FAISS 벡터 스토어 검색 서비스"""
    
    def __init__(self, vectorstore_path: str = None):
        """
        Args:
            vectorstore_path: FAISS 인덱스 경로
        """
        self.vectorstore_path = vectorstore_path or settings.VECTORSTORE_PATH
        self.embeddings = None
        self.vectorstore = None
        self._initialize()
    
    def _initialize(self):
        """벡터 스토어 초기화"""
        try:
            logger.info("벡터 스토어 초기화 중...")
            
            # 임베딩 모델 로드 (벡터화할 때와 동일한 모델 사용)
            logger.info("임베딩 모델 로딩 중...")
            self.embeddings = HuggingFaceEmbeddings(
                model_name="jhgan/ko-sroberta-multitask",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            
            # FAISS 벡터 스토어 로드
            vectorstore_path = Path(self.vectorstore_path)
            if not vectorstore_path.exists():
                raise FileNotFoundError(
                    f"벡터 스토어를 찾을 수 없습니다: {self.vectorstore_path}"
                )
            
            logger.info(f"FAISS 인덱스 로딩 중: {self.vectorstore_path}")
            self.vectorstore = FAISS.load_local(
                str(vectorstore_path),
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            
            logger.info("벡터 스토어 초기화 완료!")
            
        except Exception as e:
            logger.error(f"벡터 스토어 초기화 실패: {e}")
            raise
    
    def search(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """
        쿼리와 유사한 문서 검색
        
        Args:
            query: 검색 쿼리
            k: 반환할 문서 수
        
        Returns:
            검색된 문서 리스트 (page_content, metadata 포함)
        """
        try:
            if not self.vectorstore:
                raise RuntimeError("벡터 스토어가 초기화되지 않았습니다")
            
            # 유사도 검색
            docs = self.vectorstore.similarity_search(query, k=k)
            
            # 결과 포맷팅
            results = []
            for doc in docs:
                results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata
                })
            
            logger.info(f"검색 완료: {len(results)}개 문서 반환")
            return results
            
        except Exception as e:
            logger.error(f"검색 실패: {e}")
            raise
    
    def search_with_scores(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """
        쿼리와 유사한 문서 검색 (유사도 점수 포함)
        
        Args:
            query: 검색 쿼리
            k: 반환할 문서 수
        
        Returns:
            검색된 문서 리스트 (page_content, metadata, score 포함)
        """
        try:
            if not self.vectorstore:
                raise RuntimeError("벡터 스토어가 초기화되지 않았습니다")
            
            # 유사도 검색 with scores
            docs_with_scores = self.vectorstore.similarity_search_with_score(query, k=k)
            
            # 결과 포맷팅
            results = []
            for doc, score in docs_with_scores:
                results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": float(score)
                })
            
            logger.info(f"검색 완료: {len(results)}개 문서 반환 (점수 포함)")
            return results
            
        except Exception as e:
            logger.error(f"검색 실패: {e}")
            raise


# 전역 벡터 스토어 서비스 인스턴스
_vectorstore_service = None


def get_vectorstore_service() -> VectorStoreService:
    """벡터 스토어 서비스 싱글톤 인스턴스 반환"""
    global _vectorstore_service
    if _vectorstore_service is None:
        _vectorstore_service = VectorStoreService()
    return _vectorstore_service

