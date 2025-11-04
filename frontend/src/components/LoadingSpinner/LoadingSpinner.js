import React from 'react';

// 전체 화면 로딩 스피너
export function LoadingOverlay({ message = "로딩 중..." }) {
  return (
    <div className="loading-overlay">
      <div className="loading-spinner-container">
        <div className="loading-spinner"></div>
        <p className="loading-text">{message}</p>
      </div>
    </div>
  );
}

// 메시지 로딩 표시 (챗봇 응답 대기 중)
export function MessageLoading({ message = "답변을 생성하고 있습니다..." }) {
  return (
    <div className="message-loading">
      <div className="message-loading-spinner"></div>
      <p className="message-loading-text">{message}</p>
    </div>
  );
}

export default LoadingOverlay;