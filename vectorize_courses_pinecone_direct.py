"""
PINECONE API 직접 사용을 위한 벡터화 스크립트
LangChain 호환성 문제를 우회하여 PINECONE API v5를 직접 사용
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any
import numpy as np
from tqdm import tqdm
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# HuggingFace 임베딩 모델 사용 (한국어 특화)
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings

# PINECONE API v5 직접 사용
from pinecone import Pinecone, ServerlessSpec
import uuid
import time


class DirectPineconeVectorizer:
    """PINECONE API 직접 사용 벡터화 클래스"""
    
    def __init__(self, json_path: str = "utils/output.json"):
        """
        Args:
            json_path: 수업계획서 JSON 파일 경로
        """
        self.json_path = json_path
        self.courses_data = self._load_json()
        
        # 한국어 임베딩 모델 (jhgan/ko-sroberta-multitask)
        print("[임베딩 모델 로딩 중...]")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="jhgan/ko-sroberta-multitask",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        print("[임베딩 모델 로딩 완료!]")
        
        # PINECONE 초기화
        self._init_pinecone()
    
    def _init_pinecone(self):
        """PINECONE 초기화"""
        try:
            api_key = os.getenv("PINECONE_API_KEY")
            
            if not api_key:
                raise ValueError("PINECONE_API_KEY가 설정되지 않았습니다.")
            
            print("[PINECONE 초기화 중...]")
            self.pc = Pinecone(api_key=api_key)
            print("[PINECONE 초기화 완료!]")
            
        except Exception as e:
            print(f"[PINECONE 초기화 실패: {e}]")
            raise
    
    def _load_json(self) -> Dict:
        """JSON 파일 로드"""
        print(f"[JSON 파일 로딩: {self.json_path}]")
        with open(self.json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"[{len(data)}개 강의 데이터 로드 완료]")
        return data
    
    def _create_course_documents(self) -> List[Dict[str, Any]]:
        """각 강의를 문서 객체로 변환"""
        documents = []
        
        print("\n[강의 문서 생성 중...]")
        for course_code, course_info in tqdm(self.courses_data.items(), desc="강의 처리"):
            # 기본 정보 추출
            course_name = course_code
            professor = ""
            
            if "교과목 운영" in course_info:
                운영정보 = course_info["교과목 운영"]
                course_name = 운영정보.get("교과목", course_code)
                professor = 운영정보.get("담당교수", "")
            
            # 1. 교과목 운영 정보
            if "교과목 운영" in course_info:
                운영정보 = course_info["교과목 운영"]
                text = f"[강의명] {course_name}\n[담당교수] {professor}\n\n"
                text += "[교과목 운영]\n"
                for key, value in 운영정보.items():
                    if value and str(value) != 'nan':
                        text += f"{key}: {value}\n"
                
                documents.append({
                    "text": text,
                    "metadata": {
                        "course_name": course_name,
                        "professor": professor,
                        "section": "교과목 운영",
                        "course_code": course_code
                    }
                })
            
            # 2. 교과목 개요 (청크 분할 적용)
            if "교과목 개요" in course_info:
                개요정보 = course_info["교과목 개요"]
                text = f"[강의명] {course_name}\n[담당교수] {professor}\n\n"
                text += "[교과목 개요]\n"
                
                for key, value in 개요정보.items():
                    if key == "출석점수":
                        continue
                    if value and str(value) != 'nan':
                        text += f"{key}: {value}\n\n"
                
                # 청크 분할 적용
                chunks = self.chunk_text(text)
                for chunk_idx, chunk_text in enumerate(chunks):
                    documents.append({
                        "text": chunk_text,
                        "metadata": {
                            "course_name": course_name,
                            "professor": professor,
                            "section": "교과목 개요",
                            "course_code": course_code,
                            "chunk_id": f"outline_{chunk_idx}",
                            "chunk_index": chunk_idx,
                            "total_chunks": len(chunks)
                        }
                    })
            
            # 3. 교과목 역량
            if "교과목 역량" in course_info:
                역량정보 = course_info["교과목 역량"]
                text = f"[강의명] {course_name}\n[담당교수] {professor}\n\n"
                text += "[교과목 역량]\n"
                
                for key, value in 역량정보.items():
                    if isinstance(value, dict):
                        text += f"\n역량 {key}:\n"
                        for sub_key, sub_value in value.items():
                            if sub_value and str(sub_value) != 'nan':
                                text += f"  {sub_key}: {sub_value}\n"
                    elif value and str(value) != 'nan':
                        text += f"{key}: {value}\n"
                
                documents.append({
                    "text": text,
                    "metadata": {
                        "course_name": course_name,
                        "professor": professor,
                        "section": "교과목 역량",
                        "course_code": course_code
                    }
                })
            
            # 4. 수업계획 (주차별)
            if "수업계획" in course_info:
                수업계획 = course_info["수업계획"]
                
                # 주차별로 개별 처리 (4주씩 묶지 않음)
                weeks = sorted([k for k in 수업계획.keys() if k.endswith('주차')])
                
                for week in weeks:
                    week_info = 수업계획[week]
                    text = f"[강의명] {course_name}\n[담당교수] {professor}\n\n"
                    text += f"[{week}]\n"
                    for key, value in week_info.items():
                        if value and str(value) != 'nan':
                            text += f"{key}: {value}\n"
                    
                    # 청크 분할 적용 (주차별 내용이 길 경우)
                    chunks = self.chunk_text(text)
                    for chunk_idx, chunk_text in enumerate(chunks):
                        documents.append({
                            "text": chunk_text,
                            "metadata": {
                                "course_name": course_name,
                                "professor": professor,
                                "section": week,
                                "course_code": course_code,
                                "chunk_id": f"{week}_{chunk_idx}",
                                "chunk_index": chunk_idx,
                                "total_chunks": len(chunks)
                            }
                        })
            
            # 5. 과제 정보
            if "과제" in course_info:
                과제정보 = course_info["과제"]
                text = f"[강의명] {course_name}\n[담당교수] {professor}\n\n"
                text += "[과제 정보]\n"
                
                for key, value in 과제정보.items():
                    if isinstance(value, dict):
                        text += f"\n{key}:\n"
                        for sub_key, sub_value in value.items():
                            if sub_value and str(sub_value) != 'nan':
                                text += f"  {sub_key}: {sub_value}\n"
                    elif value and str(value) != 'nan':
                        text += f"{key}: {value}\n"
                
                documents.append({
                    "text": text,
                    "metadata": {
                        "course_name": course_name,
                        "professor": professor,
                        "section": "과제",
                        "course_code": course_code
                    }
                })
        
        # 교수님별 수업 목록 문서 생성 (추가)
        print("\n[교수님별 수업 목록 문서 생성 중...]")
        professor_courses = {}
        
        # 교수님별로 수업 수집
        for course_code, course_info in self.courses_data.items():
            if "교과목 운영" in course_info:
                운영정보 = course_info["교과목 운영"]
                professor = 운영정보.get("담당교수", "")
                course_name = 운영정보.get("교과목", course_code)
                
                if professor and professor not in professor_courses:
                    professor_courses[professor] = []
                
                if professor and course_name:
                    professor_courses[professor].append({
                        "course_name": course_name,
                        "course_code": course_code,
                        "time_credit": 운영정보.get("시간/학점", ""),
                        "classification": 운영정보.get("이수구분", ""),
                        "contact": 운영정보.get("연락처", ""),
                        "email": 운영정보.get("E-Mail", "")
                    })
        
        # 각 교수님에 대한 전용 문서 생성
        for professor, courses in professor_courses.items():
            if len(courses) > 0:  # 수업이 있는 교수님만
                text = f"[담당교수] {professor}\n"
                text += f"[담당수업수] 총 {len(courses)}개\n\n"
                
                text += "[담당수업목록]\n"
                for i, course in enumerate(courses, 1):
                    text += f"{i}. {course['course_name']} ({course['course_code']})\n"
                    text += f"   - 시간/학점: {course['time_credit']}\n"
                    text += f"   - 이수구분: {course['classification']}\n"
                    if course['contact']:
                        text += f"   - 연락처: {course['contact']}\n"
                    if course['email']:
                        text += f"   - 이메일: {course['email']}\n"
                    text += "\n"
                
                # 교수님 이름을 강조하기 위해 반복 추가
                text += f"\n{professor} 교수님의 수업입니다. {professor} 교수님이 담당하는 모든 수업입니다."
                
                documents.append({
                    "text": text,
                    "metadata": {
                        "course_name": f"{professor} 교수님 전체 수업",
                        "professor": professor,
                        "section": "교수님별 수업 목록",
                        "course_code": "PROFESSOR_LIST",
                        "course_count": len(courses)
                    }
                })
        
        print(f"[총 {len(documents)}개 문서 생성 완료]")
        return documents
    
    def create_and_save_vectorstore(self, index_name: str = "chatbot-courses", reset: bool = True):
        """
        PINECONE에 벡터 저장
        
        Args:
            index_name: Pinecone 인덱스 이름
            reset: True이면 기존 데이터 삭제 후 재생성 (기본값: True)
        """
        # 문서 생성
        documents = self._create_course_documents()
        
        print(f"\n[PINECONE 벡터 스토어 생성 중: {index_name}]")
        
        # 기존 인덱스가 있으면 삭제 (reset=True인 경우)
        if reset and index_name in self.pc.list_indexes().names():
            print(f"[기존 PINECONE 인덱스 삭제 중: {index_name}]")
            self.pc.delete_index(index_name)
            print(f"[기존 인덱스 삭제 완료]")
            time.sleep(5)  # 인덱스 삭제 완료 대기
        
        # 인덱스가 존재하지 않으면 생성
        if index_name not in self.pc.list_indexes().names():
            print(f"[PINECONE 인덱스 생성 중: {index_name}]")
            self.pc.create_index(
                name=index_name,
                dimension=768,  # ko-sroberta-multitask 임베딩 차원
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
            print(f"[PINECONE 인덱스 생성 완료: {index_name}]")
            time.sleep(10)  # 인덱스 생성 완료 대기
        
        # 인덱스 연결
        index = self.pc.Index(index_name)
        
        # 벡터 업로드를 위한 배치 처리 (최적화)
        batch_size = 200  # 배치 크기 증가
        vectors = []
        
        print(f"[벡터 생성 및 업로드 중...]")
        
        def upsert_with_retry(index, vectors, max_retries=3):
            """지수 백오프로 재시도"""
            for attempt in range(max_retries):
                try:
                    index.upsert(vectors=vectors)
                    return
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    wait_time = (2 ** attempt) * 0.5
                    print(f"[재시도 {attempt + 1}/{max_retries}] {wait_time:.1f}초 대기...")
                    time.sleep(wait_time)
        
        for i, doc in enumerate(tqdm(documents, desc="벡터 생성")):
            # 텍스트를 벡터로 변환
            embedding = self.embeddings.embed_query(doc["text"])
            
            # 벡터 추가
            vector_id = f"doc_{i}_{uuid.uuid4().hex[:8]}"
            vectors.append({
                "id": vector_id,
                "values": embedding,
                "metadata": {
                    **doc["metadata"],
                    "text": doc["text"][:1000]  # Pinecone 40KB 제한 고려
                }
            })
            
            # 배치 크기에 도달하면 업로드
            if len(vectors) >= batch_size:
                upsert_with_retry(index, vectors)
                vectors = []
                time.sleep(0.05)  # API 제한 방지 (시간 단축)
        
        # 남은 벡터 업로드
        if vectors:
            upsert_with_retry(index, vectors)
        
        print(f"[PINECONE 벡터 스토어 저장 완료: {index_name}]")
        
        # 메타데이터 통계 저장
        metadata_stats = self._get_metadata_stats(documents)
        stats_path = Path("vectorstore") / "metadata_stats.json"
        stats_path.parent.mkdir(exist_ok=True)
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(metadata_stats, indent=2, ensure_ascii=False, fp=f)
        print(f"[메타데이터 통계 저장 완료: {stats_path}]")
        
        return index
    
    def chunk_text(self, text: str, chunk_size: int = 400, overlap: int = 50) -> List[str]:
        """텍스트를 청크로 분할"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            if chunk.strip():
                chunks.append(chunk.strip())
            start = end - overlap
            if start >= len(text):
                break
        return chunks
    
    def _get_metadata_stats(self, documents: List[Dict[str, Any]]) -> Dict:
        """메타데이터 통계 정보"""
        professors = set()
        courses = set()
        sections = {}
        
        for doc in documents:
            meta = doc["metadata"]
            if meta.get('professor'):
                professors.add(meta['professor'])
            if meta.get('course_name'):
                courses.add(meta['course_name'])
            
            section = meta.get('section', 'unknown')
            sections[section] = sections.get(section, 0) + 1
        
        return {
            "total_documents": len(documents),
            "total_professors": len(professors),
            "total_courses": len(courses),
            "professors": sorted(list(professors)),
            "sections": sections
        }


def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("[수업계획서 벡터화 시작 - PINECONE 직접 사용]")
    print("=" * 60)
    
    # 벡터라이저 생성
    vectorizer = DirectPineconeVectorizer(json_path="utils/output.json")
    
    # 벡터 스토어 생성 및 저장 (기존 데이터 삭제 후 재생성)
    index = vectorizer.create_and_save_vectorstore(index_name="chatbot-courses", reset=True)
    
    print("\n" + "=" * 60)
    print("[PINECONE 벡터화 완료!]")
    print("=" * 60)
    
    # 테스트 검색
    print("\n[테스트 검색 수행 중...]")
    test_queries = [
        "C언어프로그래밍 교수님 누구야?",
        "정원석 교수님이 가르치는 과목은?",
        "C언어 수업 목표가 뭐야?",
        "C언어프로그래밍 1주차 수업 내용이 뭐야?",
        "C언어프로그래밍 5주차는 뭘 배워?"
    ]
    
    for query in test_queries:
        print(f"\n질문: {query}")
        # 쿼리를 벡터로 변환
        query_embedding = vectorizer.embeddings.embed_query(query)
        
        # PINECONE에서 검색
        results = index.query(
            vector=query_embedding,
            top_k=2,
            include_metadata=True
        )
        
        for i, match in enumerate(results.matches, 1):
            metadata = match.metadata
            print(f"  [{i}] {metadata['course_name']} - {metadata['professor']}")
            print(f"      섹션: {metadata['section']}")
            print(f"      점수: {match.score:.3f}")


if __name__ == "__main__":
    main()
