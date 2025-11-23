import React from 'react';
import './MessageItem.css';

function formatTime(ts) {
  const d = new Date(ts);
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function renderTextWithMarkdown(text, n = 16) {
  if (!text) return null;
  
  // 마크다운 굵기 표시(**텍스트**)를 <strong> 태그로 변환
  const parts = [];
  let lastIndex = 0;
  const boldRegex = /\*\*(.+?)\*\*/g;
  let match;
  let key = 0;
  let hasBold = false;
  
  while ((match = boldRegex.exec(text)) !== null) {
    hasBold = true;
    // 굵기 표시 이전 텍스트 추가
    if (match.index > lastIndex) {
      const beforeText = text.substring(lastIndex, match.index);
      parts.push(...renderTextWithWordBreaks(beforeText, n, key));
      key += beforeText.length;
    }
    
    // 굵기 표시된 텍스트를 <strong> 태그로 변환
    parts.push(<strong key={`bold-${key++}`}>{match[1]}</strong>);
    
    lastIndex = match.index + match[0].length;
  }
  
  // 남은 텍스트 추가
  if (lastIndex < text.length) {
    const remainingText = text.substring(lastIndex);
    parts.push(...renderTextWithWordBreaks(remainingText, n, key));
  }
  
  // 굵기 표시가 없으면 원래 함수 사용
  if (!hasBold) {
    return renderTextWithWordBreaks(text, n, 0);
  }
  
  return parts.length > 0 ? parts : text;
}

function renderTextWithWordBreaks(text, n = 16, startKey = 0) {
  if (!text) return [];
  const words = text.split(/(\s+)/); // split and keep spaces
  const result = [];
  let wordCount = 0;
  let key = startKey;
  
  for (let i = 0; i < words.length; i++) {
    const w = words[i];
    if (!/^\s+$/.test(w)) wordCount++;
    result.push(<span key={key++}>{w}</span>);
    if (wordCount > 0 && wordCount % n === 0 && i < words.length - 1) {
      result.push(<br key={key++} />);
    }
  }
  return result;
}

export default function MessageItem({ message }) {
  const isUser = message.from === 'user';
  if (!isUser) {
    return (
      <div className="cb-message-row bot">
        <div className="cb-message-col">
          <div className="cb-message-bubble bot">
            <div className="cb-message-text">{renderTextWithMarkdown(message.text, 16)}</div>
          </div>
          <div className="cb-message-time bot-time">{formatTime(message.ts)}</div>
        </div>
      </div>
    );
  }
  return (
    <div className="cb-message-row user">
      <div className="cb-message-col user-col">
        <div className="cb-message-bubble user">
          <div className="cb-message-text">{renderTextWithMarkdown(message.text, 16)}</div>
        </div>
        <div className="cb-message-time user-time">{formatTime(message.ts)}</div>
      </div>
    </div>
  );
}
