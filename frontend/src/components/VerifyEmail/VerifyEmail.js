import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { authAPI } from '../../utils/api';
import './VerifyEmail.css';

export default function VerifyEmail() {
  const location = useLocation();
  const navigate = useNavigate();
  const [status, setStatus] = useState('처리중...');
  const [error, setError] = useState('');

  useEffect(() => {
    async function verify() {
      const params = new URLSearchParams(location.search);
      const token = params.get('token');

      if (!token) {
        setError('유효한 검증 토큰이 없습니다.');
        setStatus('실패');
        return;
      }

      try {
        const res = await authAPI.verifyWithToken(token);
        // backend returns { success: True, data: { email: 'user@bu.ac.kr', verified: True } }
        const verifiedEmail = res?.data?.email || res?.email;
        if (verifiedEmail) {
          setStatus('인증 완료');
          
          // 새 창/팝업에서 열린 경우 부모 창에 메시지 전달 후 창 닫기
          if (window.opener && !window.opener.closed) {
            // 부모 창에 인증 완료 메시지 전달
            window.opener.postMessage({
              type: 'EMAIL_VERIFIED',
              email: verifiedEmail
            }, window.location.origin);
            
            // 부모 창으로 리다이렉트 (절대 경로 사용 - 배포 환경 호환성)
            const redirectUrl = `${window.location.origin}/signup?verifiedEmail=${encodeURIComponent(verifiedEmail)}`;
            window.opener.location.href = redirectUrl;
            
            // 팝업 창 닫기
            setTimeout(() => {
              window.close();
            }, 500);
          } else {
            // 일반 창에서 열린 경우 기존 동작 유지
            const encoded = encodeURIComponent(verifiedEmail);
            navigate(`/signup?verifiedEmail=${encoded}`);
          }
        } else {
          setError('이메일을 확인할 수 없습니다.');
          setStatus('실패');
        }
      } catch (err) {
        console.error('verify token failed', err);
        setError(err.message || '서버 오류로 인증에 실패했습니다.');
        setStatus('실패');
      }
    }

    verify();
  }, [location.search, navigate]);

  return (
    <div className="verify-page">
      <div className="verify-box">
        <h2>이메일 인증 중</h2>
        <p>{status}</p>
        {error && <p className="verify-error">{error}</p>}
      </div>
    </div>
  );
}
