import React, { useState } from 'react';
import { authAPI } from '../../utils/api';
import './Signup.css';

export default function Signup({ onSignup, onBack }) {
  const [emailPrefix, setEmailPrefix] = useState('');
  const [name, setName] = useState('');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isEmailVerified, setIsEmailVerified] = useState(false);
  const [verificationCode, setVerificationCode] = useState('');
  const [sentCode, setSentCode] = useState('');
  const [isVerifying, setIsVerifying] = useState(false);

  const fullEmail = emailPrefix ? `${emailPrefix}@bu.ac.kr` : '';

  // 이메일 인증 코드 발송
  async function handleSendVerification() {
    if (!emailPrefix.trim()) {
      setError('이메일을 입력해주세요.');
      return;
    }

    setIsVerifying(true);
    setError('');

    try {
      // 실제 API 호출
      await authAPI.sendVerificationEmail(fullEmail);
      alert(`인증번호가 ${fullEmail}로 발송되었습니다.`);
      
      // 개발용: 임시 코드 생성 (실제 환경에서는 제거)
      if (process.env.NODE_ENV === 'development') {
        const code = Math.floor(100000 + Math.random() * 900000).toString();
        setSentCode(code);
        console.log('개발용 인증코드:', code);
      }
    } catch (error) {
      console.error('Verification email failed:', error);
      setError('인증번호 발송에 실패했습니다. 다시 시도해주세요.');
      
      // 개발용 폴백: API 실패 시에도 임시 코드 생성
      if (process.env.NODE_ENV === 'development') {
        const code = Math.floor(100000 + Math.random() * 900000).toString();
        setSentCode(code);
        alert(`개발 모드: 인증번호 ${code}`);
      }
    } finally {
      setIsVerifying(false);
    }
  }

  // 인증번호 확인
  async function handleVerifyCode() {
    if (!verificationCode.trim()) {
      setError('인증번호를 입력해주세요.');
      return;
    }

    setError('');

    try {
      // 실제 API 호출
      await authAPI.verifyEmail(fullEmail, verificationCode);
      setIsEmailVerified(true);
      alert('이메일 인증이 완료되었습니다.');
    } catch (error) {
      console.error('Email verification failed:', error);
      
      // 개발용 폴백: sentCode와 비교
      if (process.env.NODE_ENV === 'development' && verificationCode === sentCode) {
        setIsEmailVerified(true);
        alert('이메일 인증이 완료되었습니다. (개발 모드)');
      } else {
        setError('인증번호가 올바르지 않습니다.');
      }
    }
  }

  async function handleSubmit(e) {
    e.preventDefault();
    
    // 유효성 검사
    if (!emailPrefix.trim()) {
      setError('이메일을 입력해주세요.');
      return;
    }
    
    if (!isEmailVerified) {
      setError('이메일 인증을 완료해주세요.');
      return;
    }
    
    if (!name.trim()) {
      setError('이름을 입력해주세요.');
      return;
    }
    
    if (!password.trim()) {
      setError('비밀번호를 입력해주세요.');
      return;
    }
    
    if (!confirm.trim()) {
      setError('비밀번호 확인을 입력해주세요.');
      return;
    }
    
    if (password !== confirm) {
      setError('비밀번호가 일치하지 않습니다.');
      return;
    }
    
    if (password.length < 6) {
      setError('비밀번호는 6자 이상이어야 합니다.');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      // 실제 API 호출 - 객체 형태로 전달
      const response = await authAPI.signup({
        email: fullEmail,
        name: name.trim(),
        password: password
      });
      
      // 회원가입 성공시 처리
      console.log('Signup successful:', response);
      alert('회원가입이 완료되었습니다. 로그인해주세요.');
      onSignup(fullEmail);
    } catch (error) {
      console.error('Signup failed:', error);
      
      if (error.response?.data?.message) {
        setError(error.response.data.message);
      } else if (error.message) {
        setError(error.message);
      } else {
        setError('회원가입에 실패했습니다. 다시 시도해주세요.');
      }
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
        
        {/* 이메일 입력 (학교 도메인 고정) */}
        <div className="email-input-group">
          <div className="email-container">
            <input
              type="text"
              placeholder="이메일 앞부분"
              value={emailPrefix}
              onChange={e => setEmailPrefix(e.target.value)}
              className="email-prefix"
              disabled={isEmailVerified}
            />
            <span className="email-suffix">@bu.ac.kr</span>
          </div>
          {!isEmailVerified ? (
            <button
              type="button"
              onClick={handleSendVerification}
              disabled={isVerifying || !emailPrefix.trim()}
              className="verify-btn"
            >
              {isVerifying ? '발송중...' : '인증번호 발송'}
            </button>
          ) : (
            <span className="verified-badge">✓ 인증완료</span>
          )}
        </div>

        {/* 인증번호 입력 (인증 완료 전까지만 표시) */}
        {sentCode && !isEmailVerified && (
          <div className="verification-group">
            <input
              type="text"
              placeholder="인증번호 6자리"
              value={verificationCode}
              onChange={e => setVerificationCode(e.target.value)}
              maxLength="6"
              className="verification-input"
            />
            <button
              type="button"
              onClick={handleVerifyCode}
              disabled={!verificationCode.trim()}
              className="verify-code-btn"
            >
              인증확인
            </button>
          </div>
        )}

        {/* 이름 입력 */}
        <input
          type="text"
          placeholder="이름"
          value={name}
          onChange={e => setName(e.target.value)}
          disabled={!isEmailVerified}
        />

        <input
          type="password"
          placeholder="비밀번호 (6자 이상)"
          value={password}
          onChange={e => setPassword(e.target.value)}
          disabled={!isEmailVerified}
        />
        <input
          type="password"
          placeholder="비밀번호 확인"
          value={confirm}
          onChange={e => setConfirm(e.target.value)}
          disabled={!isEmailVerified}
        />
        {error && <div className="signup-error">{error}</div>}
        <button type="submit" disabled={isLoading || !isEmailVerified}>
          {isLoading ? '회원가입 중...' : '회원가입'}
        </button>
      </form>
    </div>
  );
}
