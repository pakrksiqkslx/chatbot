import React, { useState } from 'react';
import './Login.css';

export default function Login({ onLogin, onSignup, onBack }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  function handleSubmit(e) {
    e.preventDefault();
    if (!email || !password) {
      setError('이메일과 비밀번호를 입력하세요.');
      return;
    }
    // 예시: 간단한 인증 로직 (실제 서비스에서는 API 호출 필요)
    if (email === 'test@test.com' && password === '1234') {
      setError('');
      onLogin(email);
    } else {
      setError('이메일 또는 비밀번호가 올바르지 않습니다.');
    }
  }

  return (
    <div className="login-container">
      {onBack && (
        <button
          type="button"
          className="back-btn"
          onClick={onBack}
        >
          ← 뒤로가기
        </button>
      )}
      <form className="login-form" onSubmit={handleSubmit}>
        <h2>로그인</h2>
        <input
          type="email"
          placeholder="이메일"
          value={email}
          onChange={e => setEmail(e.target.value)}
        />
        <input
          type="password"
          placeholder="비밀번호"
          value={password}
          onChange={e => setPassword(e.target.value)}
        />
        {error && <div className="login-error">{error}</div>}
        <button type="submit">로그인</button>
        <button
          type="button"
          className="login-signup-btn"
          onClick={onSignup}
          style={{ marginTop: 8, background: '#eee', color: '#1976d2' }}
        >
          회원가입
        </button>
      </form>
    </div>
  );
}
