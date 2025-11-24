"""
프롬프트 관리 모듈
"""
import os
from pathlib import Path
from typing import Optional

# 프롬프트 디렉토리 경로
PROMPTS_DIR = Path(__file__).parent


def load_prompt(filename: str) -> str:
    """
    프롬프트 파일을 로드합니다.
    
    Args:
        filename: 프롬프트 파일명 (예: "intent_classification.txt")
    
    Returns:
        프롬프트 텍스트
    
    Raises:
        FileNotFoundError: 프롬프트 파일을 찾을 수 없는 경우
    """
    prompt_path = PROMPTS_DIR / filename
    
    if not prompt_path.exists():
        raise FileNotFoundError(f"프롬프트 파일을 찾을 수 없습니다: {prompt_path}")
    
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read().strip()


def get_intent_classification_prompt() -> str:
    """의도 분류 프롬프트를 반환합니다."""
    return load_prompt("intent_classification.txt")


def get_course_answer_prompt() -> str:
    """수업 관련 답변 생성 프롬프트를 반환합니다."""
    return load_prompt("course_answer.txt")


def get_casual_answer_prompt() -> str:
    """일상 대화 답변 생성 프롬프트를 반환합니다."""
    return load_prompt("casual_answer.txt")

