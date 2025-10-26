import React, { useState } from 'react';
import { authAPI } from '../../utils/api';
import './Signup.css';

export default function Signup({ onSignup, onBack }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!email || !password || !confirm) {
      setError('모든 항목을 입력하세요.');
      return;
    }
    if (password !== confirm) {
      setError('비밀번호가 일치하지 않습니다.');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const response = await authAPI.signup(email, password);
      
      // 회원가입 성공시 처리
      console.log('Signup successful:', response);
      alert('회원가입이 완료되었습니다. 로그인해주세요.');
      onSignup(email);
    } catch (error) {
      console.error('Signup failed:', error);
      setError(error.message || '회원가입에 실패했습니다. 다시 시도해주세요.');
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="signup-container">
      {onBack && (
        <button
          type="button"
          className="back-btn"
          onClick={onBack}
        >
          ← 뒤로가기
        </button>
      )}
      <form className="signup-form" onSubmit={handleSubmit}>
        <h2>회원가입</h2>
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
        <input
          type="password"
          placeholder="비밀번호 확인"
          value={confirm}
          onChange={e => setConfirm(e.target.value)}
        />
        {error && <div className="signup-error">{error}</div>}
        <button type="submit" disabled={isLoading}>
          {isLoading ? '회원가입 중...' : '회원가입'}
        </button>
      </form>
    </div>
  );
}
