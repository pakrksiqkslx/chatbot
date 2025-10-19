"""
수업계획서 벡터화 및 FAISS 저장 스크립트
- 강의명과 교수명을 함께 벡터화하여 검색 정확도 향상
"""

import json
import os
import pickle
from pathlib import Path
from typing import List, Dict, Any
import numpy as np
from tqdm import tqdm

# HuggingFace 임베딩 모델 사용 (한국어 특화)
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document


class CourseVectorizer:
    """수업계획서 벡터화 클래스"""
    
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
    
    def _load_json(self) -> Dict:
        """JSON 파일 로드"""
        print(f"[JSON 파일 로딩: {self.json_path}]")
        with open(self.json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"[{len(data)}개 강의 데이터 로드 완료]")
        return data
    
    def _create_course_documents(self) -> List[Document]:
        """각 강의를 Document 객체로 변환 (강의명 + 교수명 포함)"""
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
                
                documents.append(Document(
                    page_content=text,
                    metadata={
                        "course_name": course_name,
                        "professor": professor,
                        "section": "교과목 운영",
                        "course_code": course_code
                    }
                ))
            
            # 2. 교과목 개요
            if "교과목 개요" in course_info:
                개요정보 = course_info["교과목 개요"]
                text = f"[강의명] {course_name}\n[담당교수] {professor}\n\n"
                text += "[교과목 개요]\n"
                
                for key, value in 개요정보.items():
                    if key == "출석점수":
                        continue
                    if value and str(value) != 'nan':
                        text += f"{key}: {value}\n\n"
                
                documents.append(Document(
                    page_content=text,
                    metadata={
                        "course_name": course_name,
                        "professor": professor,
                        "section": "교과목 개요",
                        "course_code": course_code
                    }
                ))
            
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
                
                documents.append(Document(
                    page_content=text,
                    metadata={
                        "course_name": course_name,
                        "professor": professor,
                        "section": "교과목 역량",
                        "course_code": course_code
                    }
                ))
            
            # 4. 수업계획 (주차별)
            if "수업계획" in course_info:
                수업계획 = course_info["수업계획"]
                
                # 주차별로 묶어서 처리 (4주씩)
                weeks = sorted([k for k in 수업계획.keys() if k.endswith('주차')])
                
                for i in range(0, len(weeks), 4):
                    week_group = weeks[i:i+4]
                    text = f"[강의명] {course_name}\n[담당교수] {professor}\n\n"
                    text += f"[수업계획 - {week_group[0]} ~ {week_group[-1]}]\n\n"
                    
                    for week in week_group:
                        week_info = 수업계획[week]
                        text += f"■ {week}\n"
                        for key, value in week_info.items():
                            if value and str(value) != 'nan':
                                text += f"  {key}: {value}\n"
                        text += "\n"
                    
                    documents.append(Document(
                        page_content=text,
                        metadata={
                            "course_name": course_name,
                            "professor": professor,
                            "section": f"수업계획_{week_group[0]}~{week_group[-1]}",
                            "course_code": course_code
                        }
                    ))
            
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
                
                documents.append(Document(
                    page_content=text,
                    metadata={
                        "course_name": course_name,
                        "professor": professor,
                        "section": "과제",
                        "course_code": course_code
                    }
                ))
        
        print(f"[총 {len(documents)}개 문서 생성 완료]")
        return documents
    
    def create_and_save_vectorstore(self, output_dir: str = "vectorstore"):
        """벡터 스토어 생성 및 저장"""
        # 문서 생성
        documents = self._create_course_documents()
        
        # FAISS 벡터 스토어 생성
        print("\n[FAISS 벡터 스토어 생성 중...]")
        vectorstore = FAISS.from_documents(
            documents=documents,
            embedding=self.embeddings
        )
        
        # 저장 디렉토리 생성
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # FAISS 인덱스 저장
        vectorstore_path = output_path / "faiss_index"
        vectorstore.save_local(str(vectorstore_path))
        print(f"[FAISS 벡터 스토어 저장 완료: {vectorstore_path}]")
        
        # 메타데이터 통계 저장
        metadata_stats = self._get_metadata_stats(documents)
        stats_path = output_path / "metadata_stats.json"
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(metadata_stats, indent=2, ensure_ascii=False, fp=f)
        print(f"[메타데이터 통계 저장 완료: {stats_path}]")
        
        return vectorstore
    
    def _get_metadata_stats(self, documents: List[Document]) -> Dict:
        """메타데이터 통계 정보"""
        professors = set()
        courses = set()
        sections = {}
        
        for doc in documents:
            meta = doc.metadata
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
    print("[수업계획서 벡터화 시작]")
    print("=" * 60)
    
    # 벡터라이저 생성
    vectorizer = CourseVectorizer(json_path="utils/output.json")
    
    # 벡터 스토어 생성 및 저장
    vectorstore = vectorizer.create_and_save_vectorstore(output_dir="vectorstore")
    
    print("\n" + "=" * 60)
    print("[벡터화 완료!]")
    print("=" * 60)
    
    # 테스트 검색
    print("\n[테스트 검색 수행 중...]")
    test_queries = [
        "C언어프로그래밍 교수님 누구야?",
        "정원석 교수님이 가르치는 과목은?",
        "C언어 수업 목표가 뭐야?"
    ]
    
    for query in test_queries:
        print(f"\n질문: {query}")
        results = vectorstore.similarity_search(query, k=2)
        for i, doc in enumerate(results, 1):
            print(f"  [{i}] {doc.metadata['course_name']} - {doc.metadata['professor']}")
            print(f"      섹션: {doc.metadata['section']}")
            print(f"      내용 미리보기: {doc.page_content[:100]}...")


if __name__ == "__main__":
    main()

