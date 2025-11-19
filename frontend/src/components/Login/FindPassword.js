import React, { useState } from 'react';
import { authAPI } from '../../utils/api';
import './Login.css';

export default function FindPassword({ onBack }) {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setMessage('');
    if (!email) {
      setMessage('이메일을 입력하세요.');
      return;
    }
    setIsLoading(true);
    try {
      // 실제 API 호출 (임시)
      await authAPI.findPassword(email);
      setMessage('비밀번호 재설정 메일이 발송되었습니다. 메일함을 확인해 주세요.');
    } catch (error) {
      setMessage(error.message || '비밀번호 찾기 요청에 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="login-container">
      <button type="button" className="back-btn" onClick={onBack}>
        ← 뒤로가기
      </button>
      <form className="login-form" onSubmit={handleSubmit}>
        <h2>비밀번호 찾기</h2>
        <input
          type="email"
          placeholder="이메일"
          value={email}
          onChange={e => setEmail(e.target.value)}
        />
        {message && <div className="login-error">{message}</div>}
        <button type="submit" disabled={isLoading} style={{ marginTop: 8 }}>
          {isLoading ? '요청 중...' : '비밀번호 찾기'}
        </button>
      </form>
    </div>
  );
}
