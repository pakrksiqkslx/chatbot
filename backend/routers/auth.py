"""
인증 관련 API 라우터
"""
from fastapi import APIRouter, HTTPException, status
from datetime import datetime, timedelta
from bson import ObjectId
import logging

from models.user import UserSignup, UserLogin, UserResponse
from database import Collections, db_instance
from auth_utils import hash_password, verify_password, create_access_token
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/signup",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="회원가입",
    description="새로운 사용자를 등록합니다."
)
async def signup(user_data: UserSignup):
    """
    회원가입 엔드포인트

    - **student_id**: 학번 (8-10자리 숫자)
    - **name**: 이름 (2-20자)
    - **email**: 이메일 (유효한 이메일 형식)
    - **password**: 비밀번호 (최소 8자, 영문+숫자+특수문자)
    - **department**: 학과 (2-50자)
    """
    try:
        # 1. 데이터베이스 연결
        users_collection = db_instance.get_collection(Collections.USERS)

        # 2. 중복 확인 (학번)
        existing_student = await users_collection.find_one({"student_id": user_data.student_id})
        if existing_student:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "success": False,
                    "error": {
                        "code": "CONFLICT",
                        "message": "이미 존재하는 학번입니다",
                        "details": f"학번 '{user_data.student_id}'은(는) 이미 등록되어 있습니다"
                    }
                }
            )

        # 3. 중복 확인 (이메일)
        existing_email = await users_collection.find_one({"email": user_data.email})
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "success": False,
                    "error": {
                        "code": "CONFLICT",
                        "message": "이미 존재하는 이메일입니다",
                        "details": f"이메일 '{user_data.email}'은(는) 이미 등록되어 있습니다"
                    }
                }
            )

        # 4. 비밀번호 해싱
        password_hash = hash_password(user_data.password)

        # 5. 사용자 문서 생성
        now = datetime.utcnow()
        user_doc = {
            "student_id": user_data.student_id,
            "name": user_data.name,
            "email": user_data.email,
            "password_hash": password_hash,
            "department": user_data.department,
            "role": "user",
            "created_at": now,
            "updated_at": now
        }

        # 6. MongoDB에 삽입
        result = await users_collection.insert_one(user_doc)
        user_id = str(result.inserted_id)

        logger.info(f"새로운 사용자 등록: {user_data.student_id} ({user_data.name})")

        # 7. 응답 생성 (API 명세서 형식)
        return {
            "success": True,
            "data": {
                "user_id": user_id,
                "student_id": user_data.student_id,
                "name": user_data.name,
                "email": user_data.email,
                "department": user_data.department,
                "created_at": now.isoformat() + "Z"
            },
            "message": "회원가입이 완료되었습니다"
        }

    except HTTPException:
        # HTTPException은 그대로 전달
        raise

    except Exception as e:
        logger.error(f"회원가입 처리 중 오류 발생: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "서버 내부 오류가 발생했습니다",
                    "details": str(e)
                }
            }
        )


@router.post(
    "/login",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="로그인",
    description="사용자 인증 후 JWT 토큰을 발급합니다."
)
async def login(credentials: UserLogin):
    """
    로그인 엔드포인트

    - **student_id**: 학번
    - **password**: 비밀번호

    **Returns**: JWT Access Token 및 사용자 정보
    """
    try:
        # 1. 데이터베이스 연결
        users_collection = db_instance.get_collection(Collections.USERS)

        # 2. 학번으로 사용자 조회
        user = await users_collection.find_one({"student_id": credentials.student_id})

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "success": False,
                    "error": {
                        "code": "UNAUTHORIZED",
                        "message": "학번 또는 비밀번호가 올바르지 않습니다",
                        "details": "입력하신 정보를 다시 확인해주세요"
                    }
                }
            )

        # 3. 비밀번호 검증
        if not verify_password(credentials.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "success": False,
                    "error": {
                        "code": "UNAUTHORIZED",
                        "message": "학번 또는 비밀번호가 올바르지 않습니다",
                        "details": "입력하신 정보를 다시 확인해주세요"
                    }
                }
            )

        # 4. JWT 토큰 생성
        access_token = create_access_token(
            data={"sub": str(user["_id"]), "student_id": user["student_id"]}
        )

        logger.info(f"사용자 로그인 성공: {credentials.student_id} ({user['name']})")

        # 5. 응답 생성 (API 명세서 형식)
        return {
            "success": True,
            "data": {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # 초 단위
                "user": {
                    "user_id": str(user["_id"]),
                    "student_id": user["student_id"],
                    "name": user["name"],
                    "email": user["email"],
                    "department": user["department"]
                }
            },
            "message": "로그인 성공"
        }

    except HTTPException:
        # HTTPException은 그대로 전달
        raise

    except Exception as e:
        logger.error(f"로그인 처리 중 오류 발생: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "서버 내부 오류가 발생했습니다",
                    "details": str(e)
                }
            }
        )
